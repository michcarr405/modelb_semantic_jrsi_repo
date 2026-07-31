import numpy as np
from modelb_semantic_repo.phase6 import norm,model,observe,corrected,panel
from modelb_semantic_repo.rng import PermutationStream

def test_default_observer_deterministic():
 m=model(norm({'n_cells':4,'n_seqs':2}));p=np.zeros((4,2,60),np.int8);a=observe(p,m,np.random.default_rng(2));b=observe(p,m,np.random.default_rng(2));assert all(np.array_equal(x,y) for x,y in zip(a,b))
def test_structural_endpoints():
 for sp in [{'motif_length':4,'n_metabolites':3},{'motif_length':6,'n_metabolites':6,'stride':5}]:
  m=model(norm({'n_cells':3,'n_seqs':2,**sp}));p=np.random.default_rng(3).integers(0,4,size=(3,2,60),dtype=np.int8);_,mot,z,s=observe(p,m,np.random.default_rng(4));pn=panel(m,7,'x');assert any(x['endpoint_type']=='constant' for x in pn);assert any(x['endpoint_type']=='identity' for x in pn);assert len({x['map_hash'] for x in pn})==len(pn)
def test_corrected_reproducible():
 r=np.random.default_rng(5);m=r.integers(0,64,500);z=r.integers(0,4,500);s=r.integers(0,4,500);a=corrected(m,z,s,10,PermutationStream(9,'x',0));b=corrected(m,z,s,10,PermutationStream(9,'x',0));assert np.allclose(a,b)
