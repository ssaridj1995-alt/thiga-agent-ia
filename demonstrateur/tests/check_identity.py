"""Run in the isolated bootstrap job with its normal /admin and /state mounts."""
import hashlib
import json
from pathlib import Path
import sys
import uuid

import httpx2

sys.path.insert(0,'/app')
from settings import DIGEST, MODEL, NAMES, PARAMS


def need(condition, code):
    if not condition:
        raise ValueError(code)


def main():
    config = json.loads(Path('/admin/credentials.json').read_bytes())
    journal = json.loads(Path('/admin/journal.json').read_bytes())
    mapping = json.loads(Path('/state/test-identities.json').read_bytes())
    marker = uuid.uuid4().hex
    need(journal['complete'] is True and mapping == {user_id: actor for actor,user_id in journal['accounts'].items()}
         and set(journal['accounts']) == set(NAMES), 'mapping')
    need(Path('/state/service_secret').read_text() == config['service_secret'],'technical_secret_mapping')
    with httpx2.Client(timeout=30,trust_env=False) as h:
        webui = 'http://webui:8080'

        def login(actor, role, password):
            response = h.post(webui+'/api/v1/auths/signin',json={'email':actor+'@thiga.example.com','password':password})
            need(response.status_code==200,'signin_'+actor)
            user = response.json()
            need(user['role']==role,'role_'+actor)
            return user

        def get(route, token):
            response = h.get(webui+route,headers={'Authorization':'Bearer '+token})
            need(response.status_code==200,'api_metadata')
            return response.json()

        def grants(rows):
            return {(row['principal_type'],row['principal_id'],row['permission']) for row in rows}

        admin=login('admin-tech','admin',config['admin_password'])
        accounts=get('/api/v1/users/all',admin['token'])['users']
        need(len(accounts)==4 and sum(row['role']=='admin' for row in accounts)==1,'account_set')
        connection, = get('/api/v1/configs/tool_servers',admin['token'])['TOOL_SERVER_CONNECTIONS']
        expected_grants={('user',user_id,'read') for user_id in mapping}
        need(connection['type']=='mcp' and connection['url']=='http://mcp:8000/mcp'
             and connection['auth_type']=='bearer' and connection['key']==config['service_secret']
             and connection['headers']=={'X-OpenWebUI-User-ID':'{{USER_ID}}','X-Thiga-Message-ID':'{{MESSAGE_ID}}'}
             and grants(connection['config']['access_grants'])==expected_grants,'mcp_config')
        model=get('/api/v1/models/model?id='+MODEL,admin['token'])
        need(model['params']==PARAMS and model['is_active'] is True and grants(model['access_grants'])==expected_grants,'model_configuration')
        tags=h.get('http://ollama:11434/api/tags').json()['models']
        need(len(tags)==1,'model_count')
        qwen,=tags
        need(qwen['name']==MODEL and qwen['digest'].removeprefix('sha256:')==DIGEST
             and qwen['details']['quantization_level']=='Q4_K_M','model_digest_or_quantization')
        identities={}
        chat_checks={}
        for actor in NAMES:
            u=login(actor,'user',config['passwords'][actor])
            need(u['id']==journal['accounts'][actor],'user_mapping')
            need(MODEL in [row['id'] for row in get('/api/models',u['token'])['data']],'private_model_visible')
            get('/api/v1/tools/id/server:mcp:thiga-rh/specs',u['token'])
            identities[actor]=u['id']
            for chat_id in json.loads(sys.argv[1] if len(sys.argv)>1 else '{}').get(actor,[]):
                uuid.UUID(chat_id)
                need(get('/api/v1/chats/'+chat_id,u['token'])['id']==chat_id,'chat_persistence')
                chat_checks[chat_id]=actor

        def mcp(actor, method, params, *, service_secret=None, principal=None):
            correlation=str(uuid.uuid4())
            response=h.post('http://mcp:8000/mcp',headers={
                'Authorization':'Bearer '+(service_secret or config['service_secret']),
                'X-OpenWebUI-User-ID':principal or identities[actor], 'X-Thiga-Message-ID':correlation,
                'Accept':'application/json, text/event-stream', 'MCP-Protocol-Version':'2025-11-25',
            },json={'jsonrpc':'2.0','id':1,'method':method,'params':params})
            return response,correlation

        negative=[]
        init={'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'thiga-check','version':'1'}}
        for name,params,wanted in (
            ('invalid_service_secret',{'service_secret':'invalid-qualification'},401),
            ('unknown_identity',{'principal':'00000000-0000-0000-0000-000000000000'},403),
        ):
            response,correlation=mcp('marc','initialize',init,**params)
            need(response.status_code==wanted,name)
            negative.append({'case':name,'status':wanted,'correlation':correlation})
        direct=[]
        for actor,tool,args,wanted in (
            ('marc','get_leave_balance',{'employee_id':'alice'},{'employee_id':'alice','leave_days':12}),
            ('marc','get_leave_balance',{'employee_id':'lea'},{'employee_id':'lea','leave_days':8}),
            ('marc','get_leave_balance',{'employee_id':'claire'},'unavailable'),
            ('marc','get_leave_balance',{'employee_id':'bob'},'unavailable'),
            ('alice','get_leave_balance',{'employee_id':'lea'},'unavailable'),
            ('alice','get_leave_balance',{'employee_id':'alice'},{'employee_id':'alice','leave_days':12}),
            ('alice','get_leave_balance',{'employee_id':'lea','actor_id':'marc'},'invalid_arguments'),
            ('bob','get_leave_balance',{'employee_id':'alice'},'unavailable'),
            ('bob','get_leave_balance',{'employee_id':'bob'},{'employee_id':'bob','leave_days':21}),
            ('marc','search_employee',{'query':'  ALICE  '},[{'employee_id':'alice','first_name':'Alice','last_name':'Exemple','job_title':'Product manager','team':'produit'}]),
            ('marc','search_employee',{'query':'Bob'},[]),
        ):
            response,correlation=mcp(actor,'tools/call',{'name':tool,'arguments':args})
            need(response.status_code==200,'mcp_call_http')
            value=json.loads(response.json()['result']['content'][0]['text'])
            need(value==wanted,'unexpected_mcp_result')
            direct.append({'actor':actor,'tool':tool,'arguments':args,'result':value,'correlation':correlation})
        print(json.dumps({'verdict':'PASS','marker':marker,'accounts':identities,'private_grants':len(expected_grants),
             'model':{k:qwen[k] for k in ('name','digest','size','details')},'params':PARAMS,'negative_auth':negative,
             'direct_mcp':direct,'chat_persistence':chat_checks,'state_hashes':{
                'identity_mapping':hashlib.sha256(Path('/state/test-identities.json').read_bytes()).hexdigest(),
                'bootstrap_journal':hashlib.sha256(Path('/admin/journal.json').read_bytes()).hexdigest(),
             }},ensure_ascii=False))


if __name__=='__main__':
    try:
        main()
    except ValueError as err:
        message=str(err)
        print(json.dumps({'verdict':'FAIL','stage':message if message.replace('_','').isalnum() and len(message)<65 else 'value_error'}))
        sys.exit(1)
    except Exception as err:
        print(json.dumps({'verdict':'FAIL','error_type':type(err).__name__}))
        sys.exit(1)
