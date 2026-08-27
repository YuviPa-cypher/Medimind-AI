from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

ROOT=Path(__file__).resolve().parent.parent
DATA=ROOT/'datasets'/'diabetes.csv'
MODEL=ROOT/'backend'/'trained_models'/'disease_model.pkl'
FEATURES=['pregnancies','glucose','blood_pressure','skin_thickness','insulin','bmi','diabetes_pedigree','age']

def generate_dataset(rows=2000):
    rng=np.random.default_rng(42)
    data=pd.DataFrame({
        'pregnancies':rng.integers(0,15,rows),'glucose':rng.normal(120,32,rows).clip(50,250),
        'blood_pressure':rng.normal(72,12,rows).clip(40,130),'skin_thickness':rng.normal(22,10,rows).clip(0,70),
        'insulin':rng.normal(100,70,rows).clip(0,800),'bmi':rng.normal(31,7,rows).clip(15,60),
        'diabetes_pedigree':rng.uniform(.05,1.5,rows),'age':rng.integers(18,85,rows)})
    score=(data.glucose>126).astype(int)*3+(data.bmi>30).astype(int)*2+(data.age>50).astype(int)+(data.diabetes_pedigree>.5).astype(int)
    data['outcome']=(score>=4).astype(int)
    return data

def train():
    DATA.parent.mkdir(exist_ok=True)
    df=generate_dataset(); df.to_csv(DATA,index=False)
    x_train,x_test,y_train,y_test=train_test_split(df[FEATURES],df.outcome,test_size=.2,random_state=42,stratify=df.outcome)
    model=RandomForestClassifier(n_estimators=150,random_state=42).fit(x_train,y_train)
    MODEL.parent.mkdir(exist_ok=True); joblib.dump({'model':model,'features':FEATURES},MODEL)
    print(f'Created {DATA} and {MODEL}; accuracy={model.score(x_test,y_test):.3f}')
if __name__=='__main__': train()
