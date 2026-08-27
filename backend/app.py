from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.database.mongodb import connect_mongodb, close_mongodb
from backend.services.database_service import DatabaseService
from backend.services.prediction_service import PredictionService
from backend.services.risk_service import RiskService
from backend.services.gemini_service import GeminiService
from backend.services.report_service import ReportService
from backend.models.user import UserCreate, LoginRequest, Token
from backend.models.prediction import PredictionRequest
from backend.models.patient import PatientCreate
from backend.models.admin import DomainRequest
from backend.utils.auth_utils import hash_password, verify_password, create_access_token, decode_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False); db=DatabaseService(); predictor=PredictionService(); risk=RiskService(); gemini=GeminiService(); reports=ReportService()
async def user_auth(c: HTTPAuthorizationCredentials = Depends(security)):
    if not c: raise HTTPException(401,'Authentication required')
    payload=decode_access_token(c.credentials); user=await db.user_by_id(payload.get('sub')) if payload else None
    if not user: raise HTTPException(401,'Invalid token')
    name=user.get('name') or user.get('email','User').split('@')[0].capitalize()
    return {'id':str(user['_id']),'email':user.get('email',''),'name':name,'role':str(user.get('role','Doctor')).capitalize()}

async def clinician(user=Depends(user_auth)):
    if user['role'] not in ('Doctor','Admin'): raise HTTPException(403,'Doctor access required')
    return user
async def admin(user=Depends(user_auth)):
    if user['role']!='Admin': raise HTTPException(403,'Admin access required')
    return user

def domain_of(email): return email.rsplit('@',1)[-1].lower()

@asynccontextmanager
async def lifespan(app):
    await connect_mongodb(); predictor.load_model()
    existing=await db.user_by_email(settings.default_doctor_email)
    if not existing and db.db is not None:
        uid=await db.create_user({'email':settings.default_doctor_email,'name':settings.default_doctor_name,'role':'Admin','hashed_password':hash_password(settings.default_doctor_password)})
        await db.add_domain(domain_of(settings.default_doctor_email),uid)
    elif existing and db.db is not None:
        updates={}
        if 'name' not in existing: updates['name']=settings.default_doctor_name
        if 'hashed_password' not in existing: updates['hashed_password']=hash_password(settings.default_doctor_password)
        if updates: await db.db.users.update_one({'_id':existing['_id']},{'$set':updates})
        await db.add_domain(domain_of(settings.default_doctor_email),str(existing['_id']))
    yield; await close_mongodb()
app=FastAPI(title=settings.app_name,lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origins,allow_credentials=True,allow_methods=['*'],allow_headers=['*'])

@app.get('/')
async def root(): return {'name':'MEDIMIND','status':'running'}
@app.get('/health')
async def health(): return {'status':'healthy','service':settings.app_name}
@app.post('/auth/register')
async def register(req:UserCreate):
    email=str(req.email).lower()
    role=str(req.role).capitalize()
    if role=='Doctor' and not await db.domain_allowed(domain_of(email)): raise HTTPException(403,'Doctor email domain is not whitelisted')
    if await db.user_by_email(email): raise HTTPException(409,'Email already registered')
    name=req.name.strip() if req.name and req.name.strip() else email.split('@')[0].capitalize()
    uid=await db.create_user({'email':email,'name':name,'role':role,'hashed_password':hash_password(req.password)})
    if role=='Patient' and db.db is not None: await db.db.patients.insert_one({'user_id':uid,'name':name,'email':email,'created_at':__import__('datetime').datetime.utcnow()})

    token=create_access_token({'sub':uid,'role':role,'name':name})
    return {'access_token':token,'token_type':'bearer','user_id':uid,'name':name,'role':role}

@app.post('/auth/login',response_model=Token)
async def login(req:LoginRequest):
    email=str(req.email).lower(); user=await db.user_by_email(email)
    if not user or not verify_password(req.password,user.get('hashed_password','')): raise HTTPException(401,'Invalid email or password')
    role=str(user.get('role','Doctor')).capitalize()
    if req.role:
        req_role=str(req.role).capitalize()
        if req_role!=role and not (role=='Admin' and req_role=='Doctor'):
            raise HTTPException(403,f'This account is registered as {role}')
    if role=='Doctor' and not await db.domain_allowed(domain_of(email)): raise HTTPException(403,'Doctor email domain is not whitelisted')
    uid=str(user['_id']); name=user.get('name') or email.split('@')[0].capitalize()
    token=create_access_token({'sub':uid,'role':role,'name':name})
    return {'access_token':token,'token_type':'bearer','user_id':uid,'name':name,'role':role}


@app.post('/predict')
async def predict(req:PredictionRequest, user=Depends(user_auth)):
    data=req.model_dump(); patient_id=data.pop('patient_id',None)
    if user['role']=='Patient':
        profile=await db.patient_profile(user['id'])
        if not profile and db.db is not None:
            patient_id=(await db.save_patient({'name':user['name'],'email':user['email'],'user_id':user['id']},user['id'])).get('mongo_id')
        elif profile:
            patient_id=str(profile['_id'])
        if not data.get('name') or data['name']=='Anonymous Patient':
            data['name']=user['name']
    else:
        if not patient_id:
            patient_id=(await db.save_patient(data,user['id'])).get('mongo_id')

    cleaned=data; result=predictor.predict(cleaned); assessment=risk.assess_risk(cleaned,result['prediction'],result['confidence']); insights=await gemini.generate_clinical_insights(cleaned,result,assessment); report=reports.generate_report(cleaned,{**result,'patient_id':patient_id},insights,assessment); pid=(await db.save_prediction({**result,**assessment,'patient_id':patient_id,'patient_name':data.get('name',user['name']),'explanation':insights['explanation'],'report_path':report},user['id'])).get('mongo_id')
    return {'patient_id':patient_id,'prediction_id':pid,'report_path':report,**result,**assessment,**insights}

@app.post('/history')
async def history(body:dict={},user=Depends(user_auth)):
    if user['role']=='Patient':
        profile=await db.patient_profile(user['id'])
        if not profile:
            return {'history':[],'count':0}
        records=await db.history(str(profile['_id']))
    else:
        pid=body.get('patient_id')
        records=await db.history(pid)
    return {'history':records,'count':len(records)}

@app.get('/patients')
async def patients(user=Depends(clinician)):
    return {'patients':await db.patients(),'count':len(await db.patients())}

@app.get('/dashboard')
async def dashboard(user=Depends(user_auth)):
    if user['role']=='Patient':
        profile=await db.patient_profile(user['id'])
        query={'patient_id':str(profile['_id'])} if profile else {'patient_id':'non_existent_id'}
        total_patients=1
    else:
        query={}
        total_patients=await db.db.patients.count_documents({}) if db.db is not None else 0

    if db.db is None:
        return {'total_patients':total_patients,'total_predictions':0,'high_risk_cases':0,'recent_reports':0,'positive_predictions':0,'negative_predictions':0}

    total_predictions=await db.db.predictions.count_documents(query)
    high_risk_cases=await db.db.predictions.count_documents({**query,'risk_level':'High'})
    recent_reports=await db.db.reports.count_documents(query)
    positive_predictions=await db.db.predictions.count_documents({**query,'prediction':1})
    negative_predictions=await db.db.predictions.count_documents({**query,'prediction':0})

    return {
        'total_patients':total_patients,
        'total_predictions':total_predictions,
        'high_risk_cases':high_risk_cases,
        'recent_reports':recent_reports,
        'positive_predictions':positive_predictions,
        'negative_predictions':negative_predictions
    }

@app.get('/admin/domains')
async def domains(user=Depends(clinician)):
    return {'domains':await db.domains()}

@app.post('/chat')
async def chat(body: dict, user=Depends(user_auth)):
    return {'reply': await gemini.chat(body.get('message', ''))}

@app.post('/admin/domains')
async def add_domain(req:DomainRequest,user=Depends(clinician)):
    domain=req.domain.strip().lower().lstrip('@')
    if '.' not in domain: raise HTTPException(400,'Enter a valid domain')
    if not await db.add_domain(domain,user['id']): raise HTTPException(409,'Domain already exists')
    return {'domain':domain}

@app.delete('/admin/domains/{domain}')
async def remove_domain(domain:str,user=Depends(clinician)):
    if not await db.remove_domain(domain): raise HTTPException(404,'Domain not found')
    return {'domain':domain}

