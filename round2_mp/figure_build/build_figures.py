"""Portable adapter around recovered plotting sources; preserves final masters."""
from pathlib import Path
import argparse, json, re, shutil, hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib import font_manager
import pandas as pd

HERE=Path(__file__).resolve().parent
R2=HERE.parent
parser=argparse.ArgumentParser()
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--font-dir',type=Path,default=HERE/'fonts')
args=parser.parse_args()
OUT=args.output.resolve(); OUT.mkdir(parents=True,exist_ok=True)
WORK=OUT/'work'; WORK.mkdir(exist_ok=True)
for name in ['inputs','outputs','reconstruction']:(WORK/name).mkdir(exist_ok=True)
for p in (HERE/'historical_plot_inputs').glob('*.json'):
    shutil.copy2(p,WORK/'inputs'/p.name)
if args.font_dir:
    for p in args.font_dir.rglob('*.ttf'):font_manager.fontManager.addfont(str(p))
native_read=pd.read_csv
reads=[]
aliases={'Figure_5_MP_PRIMARY_recovered_seed_blocks.csv':'causal_specificity_seed_blocks_64new.csv'}
def read_csv(path,*a,**kw):
    name=aliases.get(Path(path).name,Path(path).name)
    target=R2/'source_tables'/name
    if not target.exists():target=HERE/'historical_plot_inputs'/name
    if not target.exists():raise FileNotFoundError(f'Unresolved plotting input: {name}')
    reads.append({'path':str(target.relative_to(R2)),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
    return native_read(target,*a,**kw)
pd.read_csv=read_csv
native_save=Figure.savefig
current=None
def savefig(fig,path,*a,**kw):
    if Path(path).suffix!='.pdf':return
    target=OUT/current
    target.parent.mkdir(parents=True,exist_ok=True)
    native_save(fig,target,*a,**kw)
Figure.savefig=savefig
jobs=[
 ('main/Figure_3.pdf','MP_PRIMARY_BUILD_FIGURE_3_v4.py','main'),
 ('main/Figure_4.pdf','MP_PRIMARY_BUILD_FIGURE_4_v6.py','figure4'),
 ('main/Figure_5.pdf','MP_PRIMARY_BUILD_FIGURE_5_v3.py','main'),
 ('main/Figure_6.pdf','MP_PRIMARY_BUILD_FIGURE_6_v3.py','main'),
 ('main/Figure_7.pdf','MP_PRIMARY_BUILD_FIGURE_7_v2.py','main'),
 ('main/Figure_8.pdf','MP_PRIMARY_BUILD_FIGURE_8_v2.py',None),
 ('supplement/Figure_S1_MP.pdf','legacy_migration.py','s1'),
 ('supplement/Figure_S2_MP.pdf','supplement_s2_plot.py',None),
 ('supplement/Figure_S3_MP.pdf','supplement_s3_plot.py',None),
 ('supplement/Figure_S4_MP.pdf','supplement_s4_plot.py',None),
 ('supplement/Figure_S5_MP.pdf','remove_s5_title.py',None),
 ('supplement/Figure_S6_MP.pdf','remove_s6_panel_d.py',None)]
records=[]
for current,name,entry in jobs:
    plt.rcdefaults(); reads.clear()
    source=HERE/'historical_source'/name
    code=source.read_text()
    # Only routing is changed here. Plot refinements are explicitly listed below.
    code=re.sub(r"Path\('/mnt/data[^']*'\)","WORK",code)
    code=code.replace('DATA=Path("."); FIG=Path(".")','DATA=WORK; FIG=WORK')
    if name=='MP_PRIMARY_BUILD_FIGURE_8_v2.py':
        code=code.replace("'Default\\nparameter setting'","'Default'").replace("'Intermediate-coupling\\nviability'","'Intermediate-coupling'").replace("'Higher-reward\\nstrong-adaptation'","'Higher-reward'").replace("'Sparse-window\\nviability'","'Sparse-window'")
        code=code.replace('ax.set_ylim(-0.05,3.75)','ax.set_ylim(-0.05,4.1)')
        code=code.replace('rotation=14','rotation=12')
    # Non-main execution avoids historical manifests and unrelated figures.
    scope={'__name__':'_portable_figure_source','__file__':str(source),'WORK':WORK}
    exec(compile(code,str(source),'exec'),scope)
    if entry:scope[entry]()
    plt.close('all')
    records.append({'figure':current,'route':'regenerated_from_plot_source','source':name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'inputs':list(reads)})
for number in [1,2]:
    rel=f'main/Figure_{number}.pdf';(OUT/'main').mkdir(exist_ok=True)
    shutil.copy2(R2/'figures'/rel,OUT/rel)
    records.append({'figure':rel,'route':'archived_conceptual_diagram_copy','note':'No numerical source-data regeneration claimed.'})
import fitz
path=OUT/'main/Figure_4.pdf'
doc=fitz.open(path); page=doc[0]
for label in ['Future-fitness recovery fraction','Mean recovery fraction']:
    for rect in page.search_for(label):page.add_redact_annot(rect,fill=(1,1,1))
page.apply_redactions(images=0,graphics=0)
page.insert_font(fontname='arimorestored',fontfile=str(args.font_dir/'Arimo-Regular.ttf'))
for label,origin,size in [
    ('Normalized\u00a0fitness\u00a0recovery',(9.20687484741211,177.96414184570312),9.4),
    ('Mean\u00a0normalized\u00a0fitness\u00a0recovery',(279.67974853515625,183.90798950195312),8.55)]:
    page.insert_text(origin,label,fontsize=size,fontname='arimorestored',rotate=90)
temp=path.with_suffix('.tmp.pdf');doc.save(temp);doc.close();temp.replace(path)
(OUT/'BUILD_PROVENANCE.json').write_text(json.dumps({'figures':records,'note':'Figure 4 labels and Figure 8 short labels, 4.1 upper axis limit and 12-degree label rotation are reconstructed from final masters; final render equivalence is tested separately.'},indent=2)+'\n')
print(f'Built {len(records)} figure outputs at {OUT}')
