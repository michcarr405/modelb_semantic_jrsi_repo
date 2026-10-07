"""Compare rendered figure pixels with unchanged final masters."""
from pathlib import Path
import argparse,json,hashlib,importlib.metadata
import fitz
import numpy as np
parser=argparse.ArgumentParser()
parser.add_argument('--generated',type=Path,required=True)
parser.add_argument('--dpi',type=int,default=144)
args=parser.parse_args()
ref=Path(__file__).resolve().parent.parent/'figures'
generated=args.generated.resolve()
provenance=json.loads((generated/'BUILD_PROVENANCE.json').read_text())
routes={r['figure']:r['route'] for r in provenance['figures']}
records=[]
for relative,route in sorted(routes.items()):
    reference=ref/relative; actual=generated/relative
    a=fitz.open(reference);b=fitz.open(actual)
    pa=a[0].get_pixmap(matrix=fitz.Matrix(args.dpi/72,args.dpi/72),alpha=False)
    pb=b[0].get_pixmap(matrix=fitz.Matrix(args.dpi/72,args.dpi/72),alpha=False)
    shape_equal=pa.width==pb.width and pa.height==pb.height
    aa=np.frombuffer(pa.samples,dtype=np.uint8);bb=np.frombuffer(pb.samples,dtype=np.uint8)
    same=shape_equal and np.array_equal(aa,bb)
    fraction=float(np.any(aa.reshape(-1,3)!=bb.reshape(-1,3),axis=1).mean()) if shape_equal else None
    records.append({'figure':relative,'route':route,'pass':bool(same),'render_dpi':args.dpi,
        'reference_pixel_size':[pa.width,pa.height],'generated_pixel_size':[pb.width,pb.height],
        'different_pixel_fraction':fraction,'reference_sha256':hashlib.sha256(reference.read_bytes()).hexdigest(),
        'generated_sha256':hashlib.sha256(actual.read_bytes()).hexdigest()})
report={'all_passed':all(r['pass'] for r in records),'figures':records,
    'regenerated_figures':sum(r['route']=='regenerated_from_plot_source' for r in records),
    'archived_diagram_copies':sum(r['route']=='archived_conceptual_diagram_copy' for r in records),
    'environment':{n:importlib.metadata.version(n) for n in ['matplotlib','numpy','pandas','PyMuPDF']},
    'scope':'Pixel equivalence at recorded resolution, not PDF byte identity. Figures 1 and 2 are copied conceptual diagrams.'}
(generated/'FIGURE_BUILD_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='figures'},indent=2))
raise SystemExit(0 if report['all_passed'] else 1)
