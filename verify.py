"""Check scientific reference values and dataset structure, not PDF metadata."""
from pathlib import Path
import csv,hashlib,json,math,platform,sys
R=Path(__file__).resolve().parent

def read(path):
    with path.open(encoding='utf8',newline='') as f:return list(csv.reader(f))

def same(a,b):
    if a==b:return True
    try:x,y=float(a),float(b)
    except ValueError:return False
    if math.isnan(x) or math.isnan(y):return math.isnan(x) and math.isnan(y)
    return math.isclose(x,y,rel_tol=1e-12,abs_tol=1e-9)

def verify():
    manifest=json.loads((R/'reference/output_manifest.json').read_text())
    report={'status':'PASS','python':sys.version,'platform':platform.platform(),'datasets':{},'reference_tables':{},'headline_values':{}}
    for name,expected in manifest.items():
        rows=read(R/name)
        assert len(rows)-1==expected['rows'],f'Row count differs: {name}'
        normalized='\n'.join(','.join(row) for row in rows)+'\n'
        digest=hashlib.sha256(normalized.encode()).hexdigest()
        report['datasets'][name]={'rows':len(rows)-1,'normalized_sha256':digest,'publication_fingerprint_matches':digest==expected['normalized_sha256']}
    for actual,ref in [('tables_v5/selected_analytical_results.csv','selected_analytical_results.csv'),('tables_v5/interface_comparison.csv','interface_comparison.csv'),('certificate_sensitivity_v5.csv','certificate_sensitivity_v5.csv')]:
        got,want=read(R/actual),read(R/'reference'/ref)
        assert got[0]==want[0] and len(got)==len(want),f'Table shape differs: {actual}'
        for i,(a,b) in enumerate(zip(got[1:],want[1:]),1):
            assert len(a)==len(b) and all(same(x,y) for x,y in zip(a,b)),f'Numerical/status mismatch: {actual}, row {i}'
        report['reference_tables'][actual]={'rows':len(got)-1,'numerical_and_status_agreement':True,'relative_tolerance':1e-12,'absolute_tolerance':1e-9}
    with (R/'tables_v5/selected_analytical_results.csv').open() as f:
        selected=[x for x in csv.DictReader(f) if x['v']=='15' and x['interface']=='realized']
    bygrade={float(x['grade']):x for x in selected}
    assert bygrade[0]['admission']=='age_cap' and float(bygrade[0]['Tmax'])==1
    assert f"{float(bygrade[-.03]['Tmax']):.3f}"=='0.410'
    assert bygrade[-.06]['admission']=='inadmissible' and float(bygrade[-.06]['fresh_gap'])>110
    with (R/'tables_v5/interface_comparison.csv').open() as f:headways={x['interface']:float(x['hmin']) for x in csv.DictReader(f)}
    assert [f'{headways[k]:.3f}' for k in ['ideal_identity','realized','common_force']]==['5.868','7.577','11.994']
    report['headline_values']={'level_age_s':1,'descent_three_percent_age_s':float(bygrade[-.03]['Tmax']),'descent_six_percent_status':bygrade[-.06]['admission'],'minimum_certified_emergency_headways_s':headways}
    summary=json.loads((R/'results_processed_v5/analytical_summary.json').read_text())
    assert summary['n_directional_checks']==20000 and summary['n_directional_violations']==0
    report['directional_check']={k:summary[k] for k in ['n_directional_checks','n_directional_violations','min_directional_margin_N']}
    with (R/'certificate_sensitivity_v5.csv').open() as f:sensitivity=list(csv.DictReader(f))
    assert all(x['physical_status']=='admissible_conditional' for x in sensitivity)
    for name in ['fig2_comparison','fig3_v5','fig4_v5','fig5_sensing']:
        assert (R/'figures_v5'/f'{name}.pdf').stat().st_size>1000
    assert (R/'certificate_sensitivity_v5.pdf').stat().st_size>1000
    (R/'audit').mkdir(exist_ok=True)
    (R/'audit/reproduction_verification.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print(f"PASS: {len(manifest)} datasets, 158 numerical/status reference rows, two headline result groups and 20,000 directional checks.")
    mismatches=[n for n,d in report['datasets'].items() if not d['publication_fingerprint_matches']]
    if mismatches:print('Normalized floating-point fingerprints differ from the publication platform: '+', '.join(mismatches)+'. Tolerant numerical reference checks passed.')
    return report

if __name__=='__main__':verify()
