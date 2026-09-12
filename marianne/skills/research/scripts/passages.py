"""Deterministic evidence passages. Presence proves provenance, not entailment."""
import hashlib,json,re
from pathlib import Path
from html.parser import HTMLParser
VERSION='primary-passages-v3'
def sha(data):return hashlib.sha256(data).hexdigest()
class Text(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.ignore=[];self.parts=[];self.main=[];self.main_depth=0
 def handle_starttag(self,tag,attrs):
  if tag in {'script','style','noscript','svg','nav','header','footer'}:self.ignore.append(tag)
  if tag in {'main','article'}:self.main_depth+=1
  if tag in {'p','div','li','section','h1','h2','h3','h4','tr','br','pre'}:self.emit('\n')
 def handle_endtag(self,tag):
  if self.ignore:
   if tag==self.ignore[-1]:self.ignore.pop()
   return
  if tag in {'p','div','li','section','h1','h2','h3','h4','tr','pre'}:self.emit('\n')
  if tag in {'main','article'}:self.main_depth=max(0,self.main_depth-1)
 def emit(self,s):
  if self.ignore:return
  self.parts.append(s)
  if self.main_depth:self.main.append(s)
 def handle_data(self,data):self.emit(data)
def extract(raw):
 text=raw.decode('utf-8',errors='replace')
 if re.search(r'<!doctype\s+html|<html[\s>]',text,re.I):
  p=Text();p.feed(text);text=''.join(p.main or p.parts)
 lines=[' '.join(x.split()) for x in text.splitlines()];lines=[x for x in lines if x]
 # Deterministic bounded excerpts with original order; no semantic summary.
 chunks=[];current=''
 for line in lines:
  while len(line)>1400:
   if current:chunks.append(current);current=''
   cut=line.rfind(' ',0,1400);cut=cut if cut>0 else 1400
   chunks.append(line[:cut]);line=line[cut:].lstrip()
  if len(current)+len(line)+1>1400:chunks.append(current);current=''
  current=(current+'\n'+line).strip()
 if current:chunks.append(current)
 return [{'id':f'P{i:04d}','text':t} for i,t in enumerate(chunks,1)]
def make(w,evidence):
 root=w/'passages';root.mkdir(exist_ok=True);idx=[]
 for s in evidence['sources']:
  if s['kind']!='primary' or s['status']!='ok':continue
  body=(w/s['body_path']).resolve();assert body.is_relative_to(w.resolve());raw=body.read_bytes();assert sha(raw)==s['sha256']
  obj={'version':VERSION,'source_id':s['id'],'body_path':s['body_path'],'body_sha256':s['sha256'],'passages':extract(raw)}
  path=root/(s['id'].replace(':','-')+'.json');path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
  idx.append({'source_id':s['id'],'url':s['url'],'body_path':s['body_path'],'body_sha256':s['sha256'],'passage_file':str(path.relative_to(w)),'passage_file_sha256':sha(path.read_bytes()),'passage_count':len(obj['passages'])})
 (w/'passages-index.json').write_text(json.dumps({'version':VERSION,'note':'Deterministic excerpts of retained bodies, not verified claims; read full body if extraction loses important structure.','sources':idx},indent=2)+'\n')
def verify(w,evidence):
 idx=json.loads((w/'passages-index.json').read_text());assert idx['version']==VERSION
 eligible={s['id']:s for s in evidence['sources'] if s['kind']=='primary' and s['status']=='ok'}
 assert len(idx['sources'])==len(eligible);seen=set();out={}
 for row in idx['sources']:
  sid=row['source_id'];assert sid in eligible and sid not in seen;seen.add(sid);s=eligible[sid]
  assert row['body_sha256']==s['sha256'] and row['body_path']==s['body_path'] and row['url']==s['url']
  body=(w/s['body_path']).resolve();assert body.is_relative_to(w.resolve());raw=body.read_bytes();assert sha(raw)==s['sha256']
  p=(w/row['passage_file']).resolve();assert p.is_relative_to(w.resolve());assert sha(p.read_bytes())==row['passage_file_sha256']
  actual=json.loads(p.read_text());expected={'version':VERSION,'source_id':sid,'body_path':s['body_path'],'body_sha256':s['sha256'],'passages':extract(raw)}
  assert actual==expected and row['passage_count']==len(expected['passages'])
  out[sid]={p['id']:p['text'] for p in actual['passages']}
 return out
