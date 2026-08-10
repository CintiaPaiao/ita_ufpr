PRE_SOURCES={'SIGA','P4E','PROAFE','CATRIM'}
def is_pre_analysis(source):return source.upper() in PRE_SOURCES
def consolidate_factor(records):
    if not records:return {'status':'NAO_IDENTIFICADO','divergent':False,'sources':[]}
    statuses={r.get('status') for r in records}; sources=sorted({r.get('fonte') for r in records if r.get('fonte')}); div='INFORMACOES_DIVERGENTES' in statuses or ('NAO_SE_APLICA' in statuses and len(statuses)>1)
    status='INFORMACOES_DIVERGENTES' if div else 'IDENTIFICADO' if statuses&{'IDENTIFICADO','ATUALIZADO_ATENDIMENTO','AUTODECLARADO_CONTEXUALIZAR'} else next(iter(statuses)); return {'status':status,'divergent':div,'sources':sources}
