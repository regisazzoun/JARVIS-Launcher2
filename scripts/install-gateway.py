#!/usr/bin/env python3
"""Operator install: extend canonical gateway, preserve auth/memory and V1."""
import json,os,pathlib,shlex,shutil,subprocess,time,zipfile
P=pathlib.Path
if os.geteuid()!=0:raise SystemExit('Run with sudo')
source=P(__file__).resolve().parents[1];base=P('/opt/jarvis/conversation');backup=P('/var/backups')/('jarvis-jl02-'+str(time.time_ns()));backup.mkdir(mode=0o700)
for name in ('server.py','core.py','missions.py','launcher_api.py','launcher_telemetry.py'):
 p=base/'jarvis'/name
 if p.exists():shutil.copy2(p,backup/name)
server=base/'jarvis/server.py';s=server.read_text()
if 'from .launcher_api import' not in s:
 s=s.replace('from .auth import Auth','from .auth import Auth\nfrom .launcher_api import Launcher,handle_get')
 marker="                if p=='/api/session':self.send"
 replacement="                if p.startswith('/launcher2') or p.startswith('/api/launcher/'):\n                    if handle_get(self,p,q):return\n"+marker
 assert marker in s;s=s.replace(marker,replacement)
 marker="server.daemon_threads=False";assert marker in s;s=s.replace(marker,marker+'\n    server.launcher=Launcher(ROOT)')
if "p=='/api/missions/interrupt'" not in s:
 marker="                elif p=='/api/missions/resume':self.send(core.missions.resume(d['id']))"
 assert marker in s;s=s.replace(marker,marker+"\n                elif p=='/api/missions/interrupt':self.send(core.missions.interrupt(d['id']))")
server.write_text(s)
shutil.copy2(source/'backend/missions.py',base/'jarvis/missions.py')
core=base/'jarvis/core.py';code=core.read_text()
code=code.replace("status={'application':'ok','database':'ok','ollama':'indisponible'}","status={'application':'ok','database':'ok','ollama':'indisponible','busy':self.lock.locked()}")
core.write_text(code)
# Reserve room for actual tool evidence in technical missions; preserve stored memory.
if 'JL02 bounded retrieval' not in code:
 code=code.replace('            relevant=relevant[:6]', '            # JL02 bounded retrieval: keep evidence space for agent missions.\n            relevant=relevant[:2] if agent_mode else relevant[:6]')
 code=code.replace("r['content'][:1000]", "r['content'][:400 if agent_mode else 1000]")
 code=code.replace("r['content'][:800]", "r['content'][:300 if agent_mode else 800]")
 code=code.replace("('capability_status','host_policy')", "('capability_status','host_policy','host_read_file')")
 core.write_text(code)

if 'MissionInterrupted' not in code:
 marker='            for round in range(rounds+1):'
 assert marker in code;code=code.replace(marker,marker+"\n                controller=getattr(self,'missions',None)\n                if mission_id and controller and controller.is_interrupted(mission_id):\n                    from .missions import MissionInterrupted\n                    raise MissionInterrupted('Mission interrompue avant nouvelle opération')")
 marker='                message=self.transport(payload)'
 assert marker in code;code=code.replace(marker,marker+"\n                if mission_id and controller and controller.is_interrupted(mission_id):\n                    from .missions import MissionInterrupted\n                    raise MissionInterrupted('Mission interrompue après génération ; aucun nouvel outil lancé')")
 core.write_text(code)
if 'JL02 before every tool' not in code:
 marker='                for call in calls[:4]:'
 assert marker in code;code=code.replace(marker,marker+"\n                    # JL02 before every tool: cooperative interruption between batch items.\n                    if mission_id and controller and controller.is_interrupted(mission_id):\n                        from .missions import MissionInterrupted\n                        raise MissionInterrupted('Mission interrompue avant nouvel outil')")
 core.write_text(code)
shutil.copy2(source/'backend/launcher_api.py',base/'jarvis/launcher_api.py');shutil.copy2(source/'backend/telemetry.py',base/'jarvis/launcher_telemetry.py')
target=base/'launcher2';target.mkdir(mode=0o755,exist_ok=True)
for p in (source/'site').iterdir():
 if p.is_file():shutil.copyfile(p,target/p.name);(target/p.name).chmod(0o644)
with zipfile.ZipFile(target/'companion-macos.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in (source/'macos').rglob('*'):
  if p.is_file():z.write(p,'JARVIS-Launcher2/'+str(p.relative_to(source)))
 for name in ('core.js','config.json'):z.write(source/'site'/name,'JARVIS-Launcher2/site/'+name)
(target/'companion-macos.zip').chmod(0o644)
policy=P('/etc/jarvis/host-policy.json');cfg=json.loads(policy.read_text());shutil.copy2(policy,backup/'host-policy.json')
code=(source/'backend/telemetry.py').read_text()
cfg['remote_hosts']['dell-observe']['commands']['telemetry']='python3 -c '+shlex.quote(code)+' '+shlex.quote('http://'+cfg['remote_hosts']['dell-observe']['address']+':11434')
cfg['scope']['authorization']='Owner JL-02 launch: development, delegation, gateway integration and Pages publication; persistent 11B Dell grants retained'
fd=os.open(str(policy)+'.jl02',os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
with os.fdopen(fd,'w') as f:json.dump(cfg,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
os.replace(str(policy)+'.jl02',policy)
subprocess.run(['python3','-m','py_compile',str(server),str(base/'jarvis/launcher_api.py'),str(base/'jarvis/launcher_telemetry.py')],check=True)
subprocess.run(['systemctl','restart','jarvis-host-bridge','jarvis-conversation'],check=True)
print('JL-02 extension installed; protected rollback backup:',backup)
