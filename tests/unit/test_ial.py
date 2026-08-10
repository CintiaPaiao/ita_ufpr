from src.domain.ial.calculator import *
def test_ranges():
    r=rendimento_component(50,80);f=frequencia_component(5,3,[.2,.4]);p=progressao_component(30,100,6,8,.5);assert 0<=r<=1 and 0<=f<=1 and 0<=p<=1
def test_missing():assert rendimento_component(None,50) is None and progressao_component(None,100,4,8,1) is None
def test_full():
    c=calculate_ial(.5,.5,.5);assert c.coverage==100 and round(c.score,2)==50 and c.status=='COMPLETO'
def test_partial():assert calculate_ial(.5,.5,None).status.startswith('IAL PARCIAL')
def test_nc():assert calculate_ial(.5,None,None).score is None
def test_band():assert classify_band(70)=='Prioridade acadêmica intensiva'

def test_band_rounding_no_gap():
    assert classify_band(64.91)=="Prioridade acadêmica elevada"
