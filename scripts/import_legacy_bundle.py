from __future__ import annotations
import argparse
from pathlib import Path
from src.db.session import init_db, session_scope
from src.services.legacy_bundle_service import import_legacy_bundle

p=argparse.ArgumentParser(description="Importa o pacote de planilhas no modelo da Calculadora ITA 2025 para o banco PAE.")
p.add_argument("--cycle",required=True)
p.add_argument("--main",required=True)
p.add_argument("--criteria")
p.add_argument("--form")
p.add_argument("--user",default="cli")
args=p.parse_args()
init_db()
with session_scope() as s:
    out=import_legacy_bundle(s,main_filename=Path(args.main).name,main_raw=Path(args.main).read_bytes(),criteria_filename=Path(args.criteria).name if args.criteria else None,criteria_raw=Path(args.criteria).read_bytes() if args.criteria else None,form_filename=Path(args.form).name if args.form else None,form_raw=Path(args.form).read_bytes() if args.form else None,cycle_code=args.cycle,username=args.user)
print(out)
