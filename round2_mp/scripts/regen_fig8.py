from pathlib import Path
import importlib.util
import matplotlib.pyplot as plt
from PIL import Image
P=Path('/mnt/data/JRSI_R2_MP_FIGURE_MIGRATION')
spec=importlib.util.spec_from_file_location('mf',P/'make_mp_migration_figures.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
def save_fast(fig,stem,title):
 fig.savefig(m.OUT/f'{stem}.pdf',metadata={'Title':title}); fig.savefig(m.OUT/f'{stem}.svg'); fig.savefig(m.OUT/f'{stem}.eps'); fig.savefig(m.OUT/f'{stem}.png',dpi=450); plt.close(fig)
m.save=save_fast; m.fig8()
im=Image.open(m.OUT/'Figure_8_MP.png').convert('RGB'); im.save(m.OUT/'Figure_8_MP.tiff',compression='tiff_lzw',dpi=(450,450))
