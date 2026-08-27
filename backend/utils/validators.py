from typing import Any

REQUIRED = {'name': str, 'age': (int, float), 'gender': str, 'glucose': (int, float), 'blood_pressure': (int, float), 'bmi': (int, float), 'diabetes_pedigree': (int, float)}

def validate_patient_data(data: dict):
    errors = []
    for field, kind in REQUIRED.items():
        if field not in data or data[field] in ('', None): errors.append(f"Field '{field}' is required")
        elif not isinstance(data[field], kind): errors.append(f"Field '{field}' has an invalid type")
    if data.get('gender', '').lower() not in ('male', 'female', 'other'): errors.append("Field 'gender' must be male, female, or other")
    for field, low, high in [('age',1,120),('glucose',0,500),('blood_pressure',0,200),('bmi',10,70),('diabetes_pedigree',0,3)]:
        if field in data and isinstance(data[field], (int,float)) and not low <= data[field] <= high: errors.append(f"Field '{field}' is out of range")
    validated = dict(data)
    for field in ('insulin','skin_thickness','pregnancies'): validated.setdefault(field, 0)
    return not errors, errors, validated
