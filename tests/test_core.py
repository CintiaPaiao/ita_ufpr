from src.core import art19,art20,ial,crps3_allowed,DEFAULT

def test_art19_boundaries():
 assert art19(2,0)=='ATENDE';assert art19(2,1)=='NAO_ATENDE';assert art19(4,1)=='ATENDE';assert art19(5,2)=='ATENDE';assert art19(5,3)=='NAO_ATENDE'
def test_art20_e0(): assert art20(0,0)=='NAO_CALCULAVEL'
def test_art20_threshold(): assert art20(1,2)=='ATENDE' and art20(0,2)=='MENOR_50_CONTEXTUALIZAR'
def test_ial_bounds_and_complete():
 s,c,st=ial(1,1,1,DEFAULT);assert s==100 and c==1 and st=='COMPLETO'
def test_ial_partial():
 s,c,st=ial(1,1,None,DEFAULT);assert s is not None and st.startswith('PARCIAL')
def test_ial_not_calculable():
 s,c,st=ial(1,None,None,DEFAULT);assert s is None and st=='NAO_CALCULAVEL'
def test_crps_lock():
 ok,missing=crps3_allowed({});assert not ok and missing
 ok,missing=crps3_allowed({k:True for k in ['mcn_validada','maic_concluida','escuta_realizada','apoios_verificados','responsabilidade_institucional','justificativas_analisadas']});assert ok and not missing
