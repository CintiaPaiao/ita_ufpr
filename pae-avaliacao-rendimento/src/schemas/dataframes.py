import pandas as pd
REQUIRED_BASES={'beneficiarios':['GRR','NOME','CURSO'],'historico':['GRR','PERIODO','DISCIPLINA_CODIGO']}
def basic_validate(df:pd.DataFrame,required:list[str])->list[str]:
    errors=[]; missing=[c for c in required if c not in df.columns]
    if missing: errors.append(f'Colunas ausentes: {missing}')
    if 'GRR' in df.columns and df['GRR'].isna().any(): errors.append('Há GRRs ausentes.')
    return errors
