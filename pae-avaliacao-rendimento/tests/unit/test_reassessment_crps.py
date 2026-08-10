from src.domain.reassessment.compare import *
from src.domain.crps.checks import *
def test_compare():
    c=compare_cycles({'ial':70,'aprovacao':20,'rep_freq':4},{'ial':40,'aprovacao':60,'rep_freq':1});assert c['ial']['status']=='MELHOROU' and c['aprovacao']['status']=='MELHOROU'
def test_crps():
    d={k:True for k in REQ};ok,miss=crps_readiness(d,False);assert ok and not miss;ok,miss=crps_readiness(d,True);assert not ok and 'cycle_comparison_completed' in miss
