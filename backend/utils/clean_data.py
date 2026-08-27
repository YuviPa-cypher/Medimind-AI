FEATURE_COLUMNS = ['pregnancies','glucose','blood_pressure','skin_thickness','insulin','bmi','diabetes_pedigree','age']

def clean_patient_data(data):
    cleaned = dict(data)
    defaults = {'pregnancies':3,'glucose':120.0,'blood_pressure':70.0,'skin_thickness':23.0,'insulin':80.0,'bmi':32.0,'diabetes_pedigree':0.372,'age':33}
    for key, value in defaults.items(): cleaned.setdefault(key, value)
    return cleaned

def extract_feature_vector(data): return [float(data[key]) for key in FEATURE_COLUMNS]
