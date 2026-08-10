import argparse
from src.db.session import init_db,session_scope
from src.services.processing_service import process_cycle

p=argparse.ArgumentParser();p.add_argument("cycle");p.add_argument("--n",type=int,default=300);p.add_argument("--allow-incomplete",action="store_true")
a=p.parse_args();init_db()
with session_scope() as s:
    print(process_cycle(s,cycle_code=a.cycle,username="CLI",n_cases=a.n,allow_incomplete=a.allow_incomplete))
