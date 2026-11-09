import pathlib,json,urllib.request
m=json.loads(pathlib.Path('/state/test-identities.json').read_text())
key=pathlib.Path('/state/service_secret').read_text()
body={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'health','version':'1'}}}
r=urllib.request.Request('http://127.0.0.1:8000/mcp',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','Accept':'application/json, text/event-stream','Authorization':'Bearer '+key,'X-OpenWebUI-User-ID':next(iter(m))})
assert urllib.request.urlopen(r,timeout=3).status==200
