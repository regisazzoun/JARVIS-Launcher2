#!/usr/bin/env python3
"""Install Launcher assets without overwriting the canonical agent engine.
The backend is managed by JARVIS-Local-AI-Lab/agentic/engine_v2/install.py.
"""
import os
from pathlib import Path
import shutil
import zipfile
source=Path(__file__).resolve().parents[1]
base=Path('/opt/jarvis/conversation')
if os.geteuid()!=0:raise SystemExit('Run as deployment operator')
if not (base/'jarvis/mission_store.py').exists():raise SystemExit('Install the mission22 canonical backend first; no legacy engine downgrade is performed.')
target=base/'launcher2';target.mkdir(mode=0o755,exist_ok=True)
for path in (source/'site').iterdir():
    if path.is_file():shutil.copyfile(path,target/path.name);(target/path.name).chmod(0o644)
with zipfile.ZipFile(target/'companion-macos.zip','w',zipfile.ZIP_DEFLATED) as archive:
    for path in (source/'macos').rglob('*'):
        if path.is_file():archive.write(path,'JARVIS-Launcher2/'+str(path.relative_to(source)))
    for name in ('core.js','config.json'):archive.write(source/'site'/name,'JARVIS-Launcher2/site/'+name)
(target/'companion-macos.zip').chmod(0o644)
print('Launcher assets updated; backend/configuration/credentials/policy unchanged.')
