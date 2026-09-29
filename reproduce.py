"""One command to regenerate the paper's current analytical results."""
from pathlib import Path
import subprocess,sys,time
from verify import verify
R=Path(__file__).resolve().parent

def main():
    start=time.perf_counter()
    for folder in ['figures_v5','results_processed_v5','results_raw','tables_v5','sections','audit']:
        (R/folder).mkdir(exist_ok=True)
    for name in ['analytical_maps.py','selected_and_sensing.py','displacement_comparison.py','sensitivity.py','tex_values.py']:
        print(f'Generating: {name}',flush=True)
        with (R/'audit'/f'{Path(name).stem}.log').open('w',encoding='utf8') as log:
            result=subprocess.run([sys.executable,'-X','utf8',str(R/'scripts'/name)],cwd=R,stdout=log,stderr=subprocess.STDOUT)
        if result.returncode:
            print((R/'audit'/f'{Path(name).stem}.log').read_text(encoding='utf8'),file=sys.stderr)
            raise SystemExit(result.returncode)
    verify()
    print(f'Reproduction completed in {time.perf_counter()-start:.1f} seconds. See audit/reproduction_verification.json.')

if __name__=='__main__':main()
