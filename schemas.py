from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class PatientBase(BaseModel):
    name: str
    phone: str

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class CheckInRequest(BaseModel):
    name: str
    phone: str
    check_in_time: datetime

class CheckInResponse(BaseModel):
    id: int
    patient_id: int
    patient_name: str
    patient_phone: str
    check_in_time: datetime

    class Config:
        from_attributes = True

class ReservationCreate(BaseModel):
    name: str = Field(..., description="환자 이름", example="홍길동")
    phone: str = Field(..., description="전화번호", example="010-1234-5678")
    reservation_time: datetime = Field(..., description="예약 희망 시간")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "홍길동",
                "phone": "010-1234-5678",
                "reservation_time": "2024-03-20T14:30:00"
            }
        }

class ReservationResponse(BaseModel):
    id: int
    patient_id: int
    patient_name: str
    patient_phone: str
    current_time: datetime
    reservation_time: datetime

    class Config:
        from_attributes = True

class PrescriptionCreate(BaseModel):
    medicine_name: str
    dosage: str
    usage_instructions: str

class MedicalRecordCreate(BaseModel):
    patient_id: int
    diagnosis: str
    comment: Optional[str] = None
    purchase: bool = False  # Add this line
    prescriptions: List[PrescriptionCreate]

class PrescriptionResponse(BaseModel):
    id: int
    medicine_name: str
    dosage: str
    usage_instructions: str
    price: int
    created_at: datetime

    class Config:
        from_attributes = True

class MedicalRecordResponse(BaseModel):
    id: int
    patient_id: int
    checkin_id: int
    patient_name: str
    patient_phone: str
    diagnosis: str
    comment: Optional[str]
    purchase: bool
    price: int
    created_at: datetime
    prescriptions: List[PrescriptionResponse]

    class Config:
        from_attributes = True

class MedicalRecordListResponse(BaseModel):
    status: str
    data: List[MedicalRecordResponse]

class PrescriptionListResponse(BaseModel):
    status: str
    patient_info: Patient
    data: List[PrescriptionResponse]