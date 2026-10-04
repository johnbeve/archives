"""Reproduce the supplied Turtle base and supplementary OWL checks in a new directory.

Python 3 standard library; JDK 17; separately downloaded pinned ROBOT JAR.
Recorded evidence is never overwritten. No third-party code is downloaded here.
"""
import argparse,csv,hashlib,json,os,platform,shutil,subprocess,sys,tempfile
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PIN='16a73c074f3df359a7338a84b4e0788785fe06117f931bb9796e9619ea776105'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def run(args,cwd,log):
    p=subprocess.run(args,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    log.write(p.stdout); log.flush()
    if p.returncode:raise RuntimeError(f'Command failed with exit code {p.returncode}: {args[0]}; see console.log')
def summary(path,required):
    with path.open() as f: rows=list(csv.DictReader(f,delimiter='\t'))
    if len(rows)!=required or len({r['id'] for r in rows})!=required:raise RuntimeError('Missing or duplicate result rows')
    if any(r['status']!='PASS' for r in rows):raise RuntimeError('Check mismatch or execution error')
    return {'cases':len(rows),'passed':len(rows),'admissible':sum(r['profile_actual']=='true' for r in rows),
            'outside_owl2_dl':sum(r['profile_actual']=='false' for r in rows),
            'consistent':sum(r['consistent']=='true' for r in rows),
            'inconsistent':sum(r['consistent']=='false' for r in rows),
            'entailed_queries':sum(r['entailment']=='true' for r in rows),
            'not_entailed_queries':sum(r['entailment']=='false' for r in rows)}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--jar',type=Path,required=True);ap.add_argument('--output',type=Path,default=ROOT/'reproduced');a=ap.parse_args()
    jar=a.jar.resolve();out=a.output.resolve()
    if sha(jar)!=PIN:raise SystemExit('Dependency SHA-256 mismatch; refusing to execute the JAR')
    if out.exists():raise SystemExit('Output directory already exists; choose a new --output path')
    out.mkdir(parents=True)
    try:
        with (out/'console.log').open('w') as log, tempfile.TemporaryDirectory(prefix='owl2-check-') as td:
            work=Path(td)
            for folder in ['examples','queries','nonempty']:
                shutil.copytree(ROOT/folder,work/folder)
            shutil.copy(ROOT/'owl_tasks.tsv',work/'owl_tasks.tsv')
            shutil.copy(ROOT/'RunOwlChecks.java',work/'RunOwlChecks.java')
            java=shutil.which('java')
            if java is None:raise RuntimeError('JDK 17 java executable not found')
            run([java,'-Xmx1g','-cp',str(jar),'RunOwlChecks.java',str(work)],work,log)
            run([java,'-Xmx1g','-cp',str(jar),'RunOwlChecks.java',str(work/'nonempty')],work,log)
            base=summary(work/'owl_results.tsv',53);extra=summary(work/'nonempty'/'owl_results.tsv',17)
            for n in ['owl_results.tsv']:shutil.copy(work/n,out/n)
            (out/'nonempty').mkdir()
            for n in ['owl_results.tsv']:shutil.copy(work/'nonempty'/n,out/'nonempty'/n)
            cpu='unknown'; mem='unknown';limit='unknown'
            if Path('/proc/cpuinfo').exists():
                cpu=next((s.split(':',1)[1].strip() for s in Path('/proc/cpuinfo').read_text().splitlines() if s.startswith('model name')),'unknown')
            if Path('/proc/meminfo').exists():mem=Path('/proc/meminfo').read_text().splitlines()[0]
            if Path('/sys/fs/cgroup/memory.max').exists():limit=Path('/sys/fs/cgroup/memory.max').read_text().strip()
            report={'status':'PASS','execution_completed_utc':datetime.now(timezone.utc).isoformat(),
                    'base_suite':base,'supplementary_nonempty_suite':extra,
                    'environment':{'platform':platform.platform(),'python':sys.version,'java_version':subprocess.run([java,'-version'],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout.strip(),
                    'cpu':cpu,'available_processors':os.cpu_count(),'guest_memory':mem,'cgroup_memory_limit_bytes':limit,'heap':'1 GiB','configuration':'HermiT factory defaults; no explicit precomputation'},
                    'dependency':{'url':'https://github.com/ontodev/robot/releases/download/v1.9.10/robot.jar','sha256':sha(jar)},
                    'source_sha256':{n:sha(ROOT/n) for n in ['RunOwlChecks.java','run_turtle_checks.py']}}
            (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
            print(json.dumps({'base':base,'additional_nonempty':extra},indent=2))
    except Exception as e:
        (out/'FAILED.txt').write_text(str(e)+'\n');raise
if __name__=='__main__':main()
