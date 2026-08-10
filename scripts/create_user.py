import argparse, getpass
from src.db.session import init_db, session_scope
from src.security.auth import bootstrap_user

p=argparse.ArgumentParser()
p.add_argument("username")
p.add_argument("display_name")
p.add_argument("role", choices=["ADMIN","PROFISSIONAL","CHEFIA","COMISSAO","AUDITOR"])
p.add_argument("--overwrite", action="store_true")
args=p.parse_args()
password=getpass.getpass("Senha: ")
password2=getpass.getpass("Confirmar senha: ")
if password!=password2: raise SystemExit("Senhas diferentes")
init_db()
with session_scope() as s:
    bootstrap_user(s, username=args.username, display_name=args.display_name, role=args.role, password=password, overwrite=args.overwrite)
print("Usuário criado/atualizado.")
