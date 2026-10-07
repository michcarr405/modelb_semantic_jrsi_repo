from pathlib import Path
import importlib.util, shutil, json, hashlib
import matplotlib.pyplot as plt
from PIL import Image
P=Path('/mnt/data/JRSI_R2_MP_FIGURE_MIGRATION')
spec=importlib.util.spec_from_file_location('mf',P/'make_mp_migration_figures.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def save_fast(fig, stem, title):
    meta={'Title':title,'Author':'JRSI Round-2 programmatic MP migration','Subject':'Programmatic source-data figure; no generative image editing'}
    fig.savefig(m.OUT/f'{stem}.pdf',metadata=meta)
    fig.savefig(m.OUT/f'{stem}.svg')
    fig.savefig(m.OUT/f'{stem}.eps')
    fig.savefig(m.OUT/f'{stem}.png',dpi=450)
    plt.close(fig)
m.save=save_fast
m.s6(); m.s7(); m.s8()
# copy previously programmatically generated Fig 5 / S4
src=Path('/mnt/data/JRSI_R2_MP_FIGURES/figures')
for old,new in [('R2_FIGURE_5_MP_CAUSAL_SPECIFICITY','Figure_5_MP'),('R2_FIGURE_S4_MP_CAUSAL_SPECIFICITY','Figure_S4_MP')]:
    for ext in ['pdf','svg','eps','png']:
        p=src/f'{old}.{ext}'
        if p.exists(): shutil.copy2(p,m.OUT/f'{new}.{ext}')
# compact TIFFs from PNGs
for png in m.OUT.glob('*.png'):
    im=Image.open(png).convert('RGB')
    im.save(m.OUT/(png.stem+'.tiff'),compression='tiff_lzw',dpi=(450,450))
# manifest

def sh(p):
    h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
man={'source_tables':{p.name:sh(p) for p in sorted(m.DATA.glob('*'))},'figures':{p.name:sh(p) for p in sorted(m.OUT.glob('*'))},'note':'All figures generated programmatically from frozen source tables; Figure 5/S4 copied from prior programmatic 64-continuation source-data production. No generative editor used.'}
(P/'SHA256_MANIFEST.json').write_text(json.dumps(man,indent=2))
