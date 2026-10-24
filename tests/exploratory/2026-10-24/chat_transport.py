# -*- coding: utf-8 -*-
"""Temporary UI transport for manual Computer use, not product UI or a scripted eval."""
import sys,json,threading,tempfile,subprocess,hashlib,shutil,time,urllib.parse
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
ROOT=Path('/Users/larry/haoqixin'); OUT=ROOT/'tests/exploratory/2026-10-24'
sys.path.insert(0,str(ROOT/'tests'))
from run_dialogues import Server
rpc=Server(); lock=threading.Lock(); sessions={}; keep=[]
HTML='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>好奇心 · 随机画像体验</title><style>*{box-sizing:border-box}body{font:17px/1.65 system-ui;margin:0;background:#eef3f4;color:#183741}main{max-width:980px;margin:auto;padding:24px}header{position:sticky;top:0;background:#eef3f4;padding:10px 0}h1{font-size:25px;margin:0 0 8px}button,textarea{font:inherit}button{padding:9px 18px;cursor:pointer;min-height:44px}#log{display:grid;gap:18px;margin:20px 0}.message{padding:18px;background:white;border:1px solid #bdced1}.user{background:#dfefed}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit;margin:8px 0}textarea{display:block;width:100%;min-height:105px;padding:12px}button:focus-visible,textarea:focus-visible,a:focus-visible{outline:3px solid #a7461e}a{display:block;margin:8px 0}#status{font-size:14px;color:#405e65}small{display:block}footer{position:sticky;bottom:0;background:#eef3f4;padding:12px 0}</style><main><header><h1>好奇心 · 本地体验验收</h1><small>真实 Codex 模型与项目 Skill。此页仅用于人工操作，不向模型注入用户画像或标准答案。</small><button id="new">开始新对话</button><span id="name"></span><p id="status">尚未开始</p></header><div id="log"></div><div id="files"></div><footer><label for="message">你想问什么？</label><textarea id="message"></textarea><button id="send" disabled>发送</button></footer></main><script>let sid=null,busy=false;const q=id=>document.getElementById(id);q('new').onclick=async()=>{q('new').disabled=true;let r=await fetch('/new',{method:'POST'});let d=await r.json();sid=d.id;q('name').textContent=' '+sid;q('log').replaceChildren();q('files').replaceChildren();q('status').textContent=d.model+' / '+d.effort+' · 好奇心已加载';q('new').disabled=false;q('send').disabled=false;};q('send').onclick=async()=>{const text=q('message').value.trim();if(!text||busy||!sid)return;busy=true;q('send').disabled=true;const r=await fetch('/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:sid,text})});if(r.ok)q('message').value='';else q('status').textContent=await r.text();};async function refresh(){if(!sid)return;let d=await(await fetch('/state?id='+sid)).json();busy=d.busy;q('send').disabled=busy;q('new').disabled=busy;q('status').textContent=busy?'正在回答…':d.error||'本轮回答已完成';q('log').replaceChildren();for(const m of d.messages){let box=document.createElement('article');box.className='message '+m.role;let name=document.createElement('b');name.textContent=m.role==='user'?'你':'好奇心';let content=document.createElement('pre');content.textContent=m.text;box.append(name,content);q('log').append(box);}q('files').replaceChildren();for(const f of d.files){let a=document.createElement('a');a.href=f.url;a.target='_blank';a.textContent='打开生成页面：'+f.name;q('files').append(a);}}setInterval(refresh,1200);</script></html>'''
def persist(s):
 p=OUT/s['id'];p.mkdir(exist_ok=True)
 (p/'dialogue.json').write_text(json.dumps({k:v for k,v in s.items() if k not in ['workspace','thread']},ensure_ascii=False,indent=2)+'\n')
def work(s,text):
 try:
  inp=[{'type':'text','text':text}]
  if not s['turns']:inp.insert(0,{'type':'skill','name':'curiosity','path':str(ROOT/'curiosity/SKILL.md')})
  with lock:turn=rpc.turn(s['thread'],inp)
  s['turns'].append(turn)
  for item in turn['items']:
   if item.get('type')=='agentMessage':s['messages'].append({'role':'assistant','phase':item.get('phase'),'text':item.get('text','')})
  dest=OUT/s['id']/'artifacts'/('turn-'+str(len(s['turns'])));dest.mkdir(parents=True,exist_ok=True)
  for f in Path(s['workspace']).rglob('*.html'):
   if '.agents' in f.parts:continue
   relative=f.relative_to(s['workspace']);target=dest/relative;target.parent.mkdir(exist_ok=True,parents=True);shutil.copyfile(f,target)
   url='/artifact/'+s['id']+'/'+urllib.parse.quote(str(relative))
   s['files']=[x for x in s['files'] if x['name']!=str(relative)]+[{'name':str(relative),'url':url}]
 except Exception as e:s['error']=str(e)
 finally:s['busy']=False;persist(s)
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def respond(self,status,content,mime='application/json; charset=utf-8'):
  data=content.encode() if isinstance(content,str) else content;self.send_response(status);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
 def do_GET(self):
  u=urllib.parse.urlparse(self.path)
  if u.path=='/':return self.respond(200,HTML,'text/html; charset=utf-8')
  if u.path=='/state':
   sid=urllib.parse.parse_qs(u.query).get('id',[''])[0];s=sessions.get(sid)
   return self.respond(200,json.dumps({k:s[k] for k in ['busy','error','messages','files']},ensure_ascii=False)) if s else self.respond(404,'{}')
  if u.path.startswith('/artifact/'):
   _,_,sid,*parts=u.path.split('/');s=sessions.get(sid)
   if s:
    target=(Path(s['workspace'])/urllib.parse.unquote('/'.join(parts))).resolve()
    if target.is_relative_to(Path(s['workspace']).resolve()) and target.suffix=='.html' and target.is_file():return self.respond(200,target.read_bytes(),'text/html; charset=utf-8')
  self.respond(404,'not found','text/plain')
 def do_POST(self):
  if self.path=='/new':
   if any(s['busy'] for s in sessions.values()):return self.respond(409,'busy')
   tmp=tempfile.TemporaryDirectory(prefix='curiosity-roleplay-');keep.append(tmp);wd=Path(tmp.name);subprocess.run(['git','init','-q',str(wd)],check=True);(wd/'.agents/skills').mkdir(parents=True);(wd/'.agents/skills/curiosity').symlink_to(ROOT/'curiosity',target_is_directory=True)
   with lock:t=rpc.call('thread/start',{'cwd':str(wd),'ephemeral':True,'approvalPolicy':'never','sandbox':'workspace-write','developerInstructions':'文件操作仅限当前工作区；可读取所选技能及其资源，不读其他用户文件或记忆，不操作系统设置或发送外部消息。知识检索照常使用。本环境没有浏览器控制工具，生成的文件由调用端打开。','config':{'web_search':'live'}})
   sid='S'+str(len(sessions)+1);s={'id':sid,'model':t.get('model'),'effort':t.get('reasoningEffort'),'thread':t['thread']['id'],'workspace':str(wd),'messages':[],'turns':[],'files':[],'busy':False,'error':None,'skill_sha256':hashlib.sha256((ROOT/'curiosity/SKILL.md').read_bytes()).hexdigest()};sessions[sid]=s;persist(s);return self.respond(200,json.dumps({'id':sid,'model':s['model'],'effort':s['effort']}))
  if self.path=='/send':
   d=json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))));s=sessions.get(d.get('id'))
   if not s or s['busy']:return self.respond(409,'busy')
   text=d.get('text','').strip()
   if not text:return self.respond(400,'empty')
   s['busy']=True;s['messages'].append({'role':'user','text':text});persist(s);threading.Thread(target=work,args=(s,text),daemon=True).start();return self.respond(202,'{}')
  self.respond(404,'{}')
try:
 print('roleplay UI: http://127.0.0.1:8766',flush=True);ThreadingHTTPServer(('127.0.0.1',8766),Handler).serve_forever()
finally:rpc.close()
