from datetime import datetime
from bson import ObjectId
from backend.database.mongodb import get_mongodb
class DatabaseService:
    @property
    def db(self): return get_mongodb()
    async def user_by_email(self,email): return await self.db.users.find_one({'email':email}) if self.db is not None else None
    async def user_by_id(self,uid):
        if self.db is None: return None
        try: return await self.db.users.find_one({'_id':ObjectId(uid)})
        except Exception: return None
    async def create_user(self,data): return str((await self.db.users.insert_one(data)).inserted_id)
    async def patient_profile(self,uid): return await self.db.patients.find_one({'user_id':uid}) if self.db is not None else None
    async def save_patient(self,data,doctor_id=None):
        data=dict(data); data['doctor_id']=doctor_id; data['created_at']=datetime.utcnow(); return {'mongo_id':str((await self.db.patients.insert_one(data)).inserted_id)}
    async def save_prediction(self,data,doctor_id=None):
        data=dict(data); data['doctor_id']=doctor_id; data['created_at']=datetime.utcnow(); return {'mongo_id':str((await self.db.predictions.insert_one(data)).inserted_id)}
    async def history(self,pid=None):
        if self.db is None: return []
        if pid is None:
            return [dict(x, id=str(x.pop('_id'))) async for x in self.db.predictions.find().sort('created_at',-1)]
        return [dict(x, id=str(x.pop('_id'))) async for x in self.db.predictions.find({'patient_id':pid}).sort('created_at',-1)]

    async def patients(self,limit=100):
        if self.db is None: return []
        return [dict(x,id=str(x.pop('_id'))) async for x in self.db.patients.find().sort('created_at',-1).limit(limit)]
    async def domains(self):
        if self.db is None: return []
        return [dict(x,id=str(x.pop('_id'))) async for x in self.db.whitelisted_domains.find({'active':True}).sort('domain',1)]
    async def domain_allowed(self,domain): return bool(self.db is not None and await self.db.whitelisted_domains.find_one({'domain':domain,'active':True}))
    async def add_domain(self,domain,uid):
        try: await self.db.whitelisted_domains.insert_one({'domain':domain,'active':True,'added_by':uid,'created_at':datetime.utcnow()}); return True
        except Exception: return False
    async def remove_domain(self,domain): return (await self.db.whitelisted_domains.delete_one({'domain':domain})).deleted_count > 0
