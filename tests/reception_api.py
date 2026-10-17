"""Real canonical API and synthetic audio; no physical microphone claim."""
import importlib.util,json,pathlib,urllib.request,urllib.error,time,sqlite3
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=pathlib.Path('/home/adminjarvis/JARVIS/jl02-private');checks=[]
spec=importlib.util.spec_from_file_location('r','/home/adminjarvis/JARVIS/mission11/agentic/mission11/reception.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);r.login()
def check(name,value):
 assert value,name
 checks.append({'name':name,'passed':True})
for path in ['/api/launcher/resources','/api/launcher/missions','/api/launcher/events?mission=0aa1ab3057b74f10a441bc83980d4761']:
 try:urllib.request.urlopen('http://localhost:8765'+path);raise AssertionError('Unauthenticated access allowed')
 except urllib.error.HTTPError as e:check('auth_required_'+path.split('?')[0],e.code==401)
try:r.client.open(urllib.request.Request('http://localhost:8765/api/launcher/missions',headers={'Origin':'https://evil.invalid'}));raise AssertionError('Origin allowed')
except urllib.error.HTTPError as e:check('foreign_origin_denied',e.code==403)
for path in ['/etc/shadow','/var/lib/jarvis/projects/../../etc/passwd']:
 try:r.call('/api/launcher/artifact?path='+urllib.parse.quote(path));raise AssertionError('Private path allowed')
 except urllib.error.HTTPError as e:check('artifact_path_confined',e.code==403)
resources=r.call('/api/launcher/resources');check('real_mac_and_dell',resources['machines']['mac-mini']['available'] and resources['machines']['dell-1']['available']);check('dell2_unavailable',not resources['machines']['dell-2']['available'])
req=urllib.request.Request('http://localhost:8765/api/tts',data=json.dumps({'text':'Bonjour Jarvis. Réponds simplement bonjour.'}).encode(),headers={'Content-Type':'application/json','X-Jarvis-Request':'1'});wav=r.client.open(req,timeout=90).read();(OUT/'voice-fixture.wav').write_bytes(wav);check('real_piper_wav',wav[:4]==b'RIFF' and len(wav)>1000)
req=urllib.request.Request('http://localhost:8765/api/stt',data=wav,headers={'Content-Type':'audio/wav','X-Jarvis-Request':'1'});transcript=json.load(r.client.open(req,timeout=120));check('real_whisper_transcription',bool(transcript.get('text','').strip()))
# Verify pause/resume persistence without executing an unrelated task: create one queued run,
# interrupt before worker pickup, then resume and immediately interrupt again.
job=r.call('/api/missions',{'goal':'JL-02 réception du contrôle de reprise uniquement. Ne modifie rien. Enregistre intervention_report du test de reprise.','model':'qwen3.5:27b-q4_K_M'})
r.call('/api/missions/interrupt',{'id':job['id']});resumed=r.call('/api/missions/resume',{'id':job['id']});check('resume_interrupted_mission',resumed['state']=='queued');r.call('/api/missions/interrupt',{'id':job['id']})
check('v1_gateway_root_preserved',r.client.open('http://localhost:8765/').status==200)
(ROOT/'docs/evidence').mkdir(parents=True,exist_ok=True);(ROOT/'docs/evidence/api-checks.json').write_text(json.dumps({'checks':checks,'audio':'Piper synthetic WAV -> Whisper real, no physical microphone','pause_test_id':job['id']},ensure_ascii=False,indent=2)+'\n');print(json.dumps(checks))
