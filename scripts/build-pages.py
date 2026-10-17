#!/usr/bin/env python3
import pathlib,shutil,zipfile
root=pathlib.Path(__file__).resolve().parents[1];out=root/'dist/pages';out.mkdir(parents=True,exist_ok=True)
for p in (root/'site').iterdir():
 if p.is_file():shutil.copyfile(p,out/p.name)
(out/'.nojekyll').touch()
with zipfile.ZipFile(out/'companion-macos.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in (root/'macos').rglob('*'):
  if p.is_file():z.write(p,'JARVIS-Launcher2/'+str(p.relative_to(root)))
 for name in ('core.js','config.json'):z.write(root/'site'/name,'JARVIS-Launcher2/site/'+name)
print(out)
