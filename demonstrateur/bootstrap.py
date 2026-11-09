import fcntl, os, pathlib, sys, uuid
import httpx2
from state import read, atomic
from settings import MODEL, PARAMS, NAMES, DIGEST

def check(value, code):
    if not value: raise ValueError(code)

def norm(grants):
    return sorted([{k:g[k] for k in ('principal_type','principal_id','permission')} for g in grants],key=str)

def main():
    c=read('/admin/credentials.json')
    path=pathlib.Path('/admin/journal.json')
    j=read(path) if path.exists() else {'accounts':{},'intents':[]}
    save=lambda: atomic(path,j)
    with httpx2.Client(base_url='http://webui:8080',timeout=120,trust_env=False) as h:
        def req(route,body=None):
            r=h.get(route) if body is None else h.post(route,json=body)
            check(r.status_code==200,'api_status_'+str(r.status_code))
            return r.json()
        admin=req('/api/v1/auths/signin',{'email':'admin-tech@thiga.example.com','password':c['admin_password']})
        check(admin['role']=='admin','admin_role')
        h.headers['Authorization']='Bearer '+admin['token']
        users=req('/api/v1/users/all')['users']
        check(len(users)<=4,'unexpected_accounts')
        for n in NAMES:
            email=n+'@thiga.example.com'
            matches=[u for u in users if u['email']==email]
            check(len(matches)<=1,'duplicate_account')
            if n in j['accounts']:
                check(len(matches)==1 and matches[0]['id']==j['accounts'][n],'uuid_divergence')
                u=matches[0]
            elif matches:
                check(n in j['intents'],'unowned_account')
                # A pending create is recoverable only with the recorded random password.
                r=h.post('/api/v1/auths/signin',json={'email':email,'password':c['passwords'][n]})
                check(r.status_code==200,'pending_ownership')
                u=r.json();check(u['id']==matches[0]['id'],'pending_uuid')
            else:
                if n not in j['intents']:j['intents'].append(n);save()
                u=req('/api/v1/auths/add',{'email':email,'name':n.capitalize(),'password':c['passwords'][n],'role':'user'})
            check(u['role']=='user' and u['id']!=admin['id'],'business_role')
            uuid.UUID(u['id'])
            j['accounts'][n]=u['id'];save()
            # Controlled interruption test hook, disabled in the delivered Compose.
            if os.getenv('THIGA_TEST_PAUSE_AFTER_ACCOUNT')==n:
                import time
                print('{"event":"test_pause_after_account"}',flush=True);time.sleep(300)
        expected={v:k for k,v in j['accounts'].items()}
        mp=pathlib.Path('/state/test-identities.json')
        if mp.exists():check(read(mp)==expected,'mapping_divergence')
        else:atomic(mp,expected,10001)
        check(pathlib.Path('/state/service_secret').read_text()==c['service_secret'],'service_secret_divergence')
        grants=[{'principal_type':'user','principal_id':j['accounts'][n],'permission':'read'} for n in NAMES]
        conn={'type':'mcp','url':'http://mcp:8000/mcp','path':'','auth_type':'bearer','key':c['service_secret'],
              'forward_cookies':False,'headers':{'X-OpenWebUI-User-ID':'{{USER_ID}}','X-Thiga-Message-ID':'{{MESSAGE_ID}}'},
              'config':{'enable':True,'function_name_filter_list':'','access_grants':grants},
              'info':{'id':'thiga-rh','name':'THIGA RH','description':'Donnees RH fictives'}}
        old=req('/api/v1/configs/tool_servers')['TOOL_SERVER_CONNECTIONS']
        if not old:
            check(not j.get('complete'),'missing_connection')
            req('/api/v1/configs/tool_servers',{'TOOL_SERVER_CONNECTIONS':[conn]})
            old=req('/api/v1/configs/tool_servers')['TOOL_SERVER_CONNECTIONS']
        check(old==[conn],'connection_divergence')
        r=h.get('/api/v1/models/model',params={'id':MODEL})
        if r.status_code==404:
            check(not j.get('complete'),'missing_model')
            j['model_intent']=True;save()
            model=req('/api/v1/models/model/access/update',{'id':MODEL,'name':MODEL,'access_grants':grants})
        else:
            check(r.status_code==200,'model_read');model=r.json()
            check(j.get('model_intent'),'unowned_model')
        check(model['id']==MODEL and model['name']==MODEL and model.get('base_model_id') is None and model['is_active'],'model_identity_divergence')
        check(norm(model['access_grants'])==norm(grants),'model_grant_divergence')
        if model['params']!=PARAMS:
            check(not j.get('complete') and model['params']=={},'parameter_divergence')
            body={k:model[k] for k in ('id','name','meta','is_active','base_model_id')};body['params']=PARAMS
            model=req('/api/v1/models/model/update',body)
        check(model['params']==PARAMS,'parameter_roundtrip')
        tags=httpx2.get('http://ollama:11434/api/tags',timeout=30,trust_env=False).json()['models']
        selected=[t for t in tags if t['name']==MODEL]
        check(len(selected)==1 and selected[0]['digest'].removeprefix('sha256:')==DIGEST,'model_digest_divergence')
        j['complete']=True;save()
        print('{"event":"bootstrap_complete","accounts":3,"private_grants":3}',flush=True)

if __name__=='__main__':
    try:
        with open('/admin/lock','a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX);main()
    except Exception as e:
        # Never serialize HTTP bodies, credentials, headers or exception messages.
        print('{"event":"bootstrap_failed","error_type":"'+type(e).__name__+'"}',flush=True)
        sys.exit(1)
