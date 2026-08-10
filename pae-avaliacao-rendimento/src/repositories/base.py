from sqlalchemy import select
class Repository:
    def __init__(self,session,model):self.session=session;self.model=model
    def get(self,obj_id):return self.session.get(self.model,obj_id)
    def list(self,limit=500):return list(self.session.scalars(select(self.model).limit(limit)))
    def add(self,obj):self.session.add(obj);self.session.flush();return obj
    def delete(self,obj):self.session.delete(obj)
