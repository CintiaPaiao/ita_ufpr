from src.domain.mcn.rules import *
def test_art17():
    assert calcular_art17(True,False).status=='ATENDE';assert calcular_art17(False,False).status=='NAO_ATENDE'
def test_art18():assert calcular_art18(300,None,None).status=='PARAMETRO_NAO_CONFIRMADO'
def test_art19():
    assert calcular_art19(2,1).status=='NAO_ATENDE';assert calcular_art19(4,1).status=='ATENDE';assert calcular_art19(5,3).status=='NAO_ATENDE'
def test_art20_zero():assert calcular_art20([{'cancelado':True,'aprovado':False}]).status=='NAO_CALCULAVEL'
def test_art21():assert calcular_art21(10,8).status=='ATENDE' and calcular_art21(13,8).status=='NAO_ATENDE'
