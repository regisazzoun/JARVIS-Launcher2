"""Measured host resources only. No hardware serials or user data."""
import glob,json,os,subprocess,time,urllib.request

def collect(ollama_url='http://127.0.0.1:11434'):
    def ticks():
        v=list(map(int,open('/proc/stat').readline().split()[1:]));return sum(v[:8]),v[3]+v[4]
    a,ai=ticks();time.sleep(.15);b,bi=ticks()
    mem={line.split(':')[0]:int(line.split()[1]) for line in open('/proc/meminfo')}
    data={'available':True,'sampled_at':time.time(),'cpu_percent':round(100*(1-(bi-ai)/(b-a)),1) if b>a else None,'cpu_threads':os.cpu_count(),'load1':os.getloadavg()[0], 'ram_total_mb':round(mem['MemTotal']/1024),'ram_used_mb':round((mem['MemTotal']-mem['MemAvailable'])/1024),'gpu':None,'ollama':False,'active_models':[]}
    try:
        r=subprocess.run(['nvidia-smi','--query-gpu=name,utilization.gpu,temperature.gpu,memory.used,memory.total','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=4)
        if r.returncode==0:
            p=[x.strip() for x in r.stdout.splitlines()[0].split(',')];data['gpu']={'name':p[0],'utilization':float(p[1]),'temperature':float(p[2]),'vram_used_mb':float(p[3]),'vram_total_mb':float(p[4])}
    except (OSError,ValueError,IndexError,subprocess.TimeoutExpired):pass
    try:
        with urllib.request.urlopen(ollama_url+'/api/ps',timeout=3) as r:active=json.load(r)
        data['ollama']=True;data['active_models']=[m['name'] for m in active.get('models',[])]
    except Exception:pass
    return data
if __name__=='__main__':
    import sys
    print(json.dumps(collect(sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:11434')))
