def delta_status(old,new,lower_is_better=True):
    if old is None or new is None:return 'DADO_INSUFICIENTE'
    if new==old:return 'ESTAVEL'
    return ('MELHOROU' if new<old else 'AGRAVOU') if lower_is_better else ('MELHOROU' if new>old else 'AGRAVOU')
def compare_cycles(previous,current):return {'ial':{'anterior':previous.get('ial'),'atual':current.get('ial'),'status':delta_status(previous.get('ial'),current.get('ial'),True)},'aprovacao':{'anterior':previous.get('aprovacao'),'atual':current.get('aprovacao'),'status':delta_status(previous.get('aprovacao'),current.get('aprovacao'),False)},'rep_freq':{'anterior':previous.get('rep_freq'),'atual':current.get('rep_freq'),'status':delta_status(previous.get('rep_freq'),current.get('rep_freq'),True)}}
def detect_quantitative_persistence(previous_mcn,current_mcn):return bool(set(previous_mcn)&set(current_mcn))
