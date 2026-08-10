import pandas as pd
from src.validation.normalization import validar_grr
def data_quality_report(df,key='GRR'):
    issues=[]
    if key not in df.columns: return pd.DataFrame([{'tipo':'COLUNA_AUSENTE','detalhe':key,'severidade':'CRITICA'}])
    for idx,v in df[key].items():
        if not validar_grr(v): issues.append({'linha':idx,'tipo':'GRR_INVALIDO','detalhe':str(v),'severidade':'CRITICA'})
    for idx,row in df[df[key].duplicated(keep=False)].iterrows(): issues.append({'linha':idx,'tipo':'GRR_DUPLICADO','detalhe':row[key],'severidade':'ALTA'})
    return pd.DataFrame(issues)
