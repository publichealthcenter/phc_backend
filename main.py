from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
import models, schemas
from config import MEDICINE_PRICES, BASE_CONSULTATION_FEE
from database import engine, get_db
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List

models.Base.metadata.create_all(bind=engine)

from api_docs import api_metadata, examples, endpoint_descriptions, parameter_descriptions

# FastAPI 인스턴스 생성 부분만 수정
app = FastAPI(**api_metadata)

# CORS 미들웨어 설정
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://180.65.58.182:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# 1. 접수하기
@app.post("/checkin", response_model=schemas.CheckInResponse,
          summary=endpoint_descriptions["checkin"]["summary"],
    description=endpoint_descriptions["checkin"]["description"],
    response_description=endpoint_descriptions["checkin"]["response_description"],
    tags=["접수"])
async def check_in(request: schemas.CheckInRequest, db: Session = Depends(get_db)):
    try:
        patient = db.query(models.Patient).filter(models.Patient.phone == request.phone).first()
        if not patient:
            patient = models.Patient(
                name=request.name,
                phone=request.phone,
                created_at=datetime.now()
            )
            db.add(patient)
            db.commit()
            db.refresh(patient)

        db_checkin = models.CheckIn(
            patient_id=patient.id,
            check_in_time=request.check_in_time
        )
        db.add(db_checkin)
        db.commit()
        db.refresh(db_checkin)

        return {
            "id": db_checkin.id,
            "patient_id": patient.id,
            "patient_name": patient.name,
            "patient_phone": patient.phone,
            "check_in_time": db_checkin.check_in_time
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 2. 전체 환자 접수 조회
@app.get("/checkins", summary=endpoint_descriptions["get_checkins"]["summary"],
    description=endpoint_descriptions["get_checkins"]["description"],
    response_description=endpoint_descriptions["get_checkins"]["response_description"],
    tags=["접수"])
async def get_all_checkins(db: Session = Depends(get_db)):
    try:
        checkins = db.query(models.CheckIn).join(models.Patient).all()
        return {
            "status": "success",
            "data": [
                {
                    "id": checkin.id,
                    "patient_id": checkin.patient_id,
                    "patient_name": checkin.patient.name,
                } for checkin in checkins
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/reservation", response_model=schemas.ReservationResponse,
          summary=endpoint_descriptions["create_reservation"]["summary"],
          description=endpoint_descriptions["create_reservation"]["description"],
          response_description=endpoint_descriptions["create_reservation"]["response_description"],
          tags=["예약"]
          )
async def create_reservation(request: schemas.ReservationCreate, db: Session = Depends(get_db)):
    try:
        patient = db.query(models.Patient).filter(models.Patient.phone == request.phone).first()
        if not patient:
            patient = models.Patient(
                name=request.name,
                phone=request.phone,
                created_at=datetime.now()
            )
            db.add(patient)
            db.commit()
            db.refresh(patient)

        # 2. 예약 생성
        reservation = models.Reservation(
            patient_id=patient.id,
            current_time=datetime.now(),  # 예약 생성 시간
            reservation_time=request.reservation_time  # 실제 예약 시간
        )
        db.add(reservation)
        db.commit()
        db.refresh(reservation)

        # 3. 응답 반환
        return {
            "id": reservation.id,
            "patient_id": patient.id,
            "patient_name": patient.name,
            "patient_phone": patient.phone,
            "current_time": reservation.current_time,
            "reservation_time": reservation.reservation_time
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/reservation/{phone}",
         summary=endpoint_descriptions["get_reservation"]["summary"],
         description=endpoint_descriptions["get_reservation"]["description"],
         response_description=endpoint_descriptions["get_reservation"]["response_description"],
         tags=["예약"]
         )
async def inquiry_reservation(phone: str, db: Session = Depends(get_db)):
    try:
        reservation = db.query(models.Reservation) \
            .join(models.Patient) \
            .filter(models.Patient.phone == phone) \
            .order_by(models.Reservation.reservation_time.desc()) \
            .first()

        if not reservation:
            raise HTTPException(status_code=404, detail="예약을 찾을 수 없습니다")

        return {
            "status": "success",
            "data": {
                "id": reservation.id,
                "patient_id": reservation.patient_id,
                "patient_name": reservation.patient.name,
                "patient_phone": reservation.patient.phone,
                "current_time": reservation.current_time,
                "reservation_time": reservation.reservation_time
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/medical-records/{patient_id}",
         summary=endpoint_descriptions["get_medical_records_by_patient_id"]["summary"],
         description=endpoint_descriptions["get_medical_records_by_patient_id"]["description"],
         response_description=endpoint_descriptions["get_medical_records_by_patient_id"]["response_description"],
         tags=["진료"]
         )
async def get_patient_records(patient_id: int, db: Session = Depends(get_db)):
    try:
        records = (
            db.query(models.MedicalRecord)
            .filter(models.MedicalRecord.patient_id == patient_id)
            .options(joinedload(models.MedicalRecord.prescriptions))
            .order_by(models.MedicalRecord.created_at.desc())
            .all()
        )

        if not records:
            raise HTTPException(status_code=404, detail="진료 기록을 찾을 수 없습니다")

        return {
            "status": "success",
            "data": [
                {
                    "id": record.id,
                    "patient_name": record.patient.name,
                    "patient_phone": record.patient.phone,
                    "diagnosis": record.diagnosis,
                    "comment": record.comment,
                    "created_at": record.created_at,
                    "prescriptions": [
                        {
                            "id": prescription.id,
                            "medicine_name": prescription.medicine_name,
                            "dosage": prescription.dosage,
                            "usage_instructions": prescription.usage_instructions,
                            "created_at": prescription.created_at
                        } for prescription in record.prescriptions
                    ]
                } for record in records
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/medical-records/phone/{phone}", response_model=schemas.MedicalRecordListResponse)
async def get_medical_records_by_phone(phone: str, db: Session = Depends(get_db)):
    try:
        patient = db.query(models.Patient).filter(models.Patient.phone == phone).first()
        
        if not patient:
            raise HTTPException(status_code=404, detail="해당 전화번호의 환자를 찾을 수 없습니다")

        records = (
            db.query(models.MedicalRecord)
            .filter(models.MedicalRecord.patient_id == patient.id)
            .options(joinedload(models.MedicalRecord.prescriptions))
            .order_by(models.MedicalRecord.created_at.desc())
            .all()
        )

        if not records:
            raise HTTPException(status_code=404, detail="해당 환자의 진료 기록을 찾을 수 없습니다")

        result_data = []
        for record in records:
            # 처방전별 가격 계산
            prescription_data = []
            total_medicine_price = 0
            
            for p in record.prescriptions:
                medicine_price = MEDICINE_PRICES.get(p.medicine_name, 0)
                total_medicine_price += medicine_price
                prescription_data.append({
                    "id": p.id,
                    "medicine_name": p.medicine_name,
                    "dosage": p.dosage,
                    "usage_instructions": p.usage_instructions,
                    "price": medicine_price,
                    "created_at": p.created_at
                })

            # 총 진료비 계산 (기본 진찰료 + 약품 가격)
            total_price = BASE_CONSULTATION_FEE + total_medicine_price

            result_data.append({
                "id": record.id,
                "patient_id": patient.id,
                "checkin_id": record.checkin_id,
                "patient_name": patient.name,
                "patient_phone": patient.phone,
                "diagnosis": record.diagnosis,
                "comment": record.comment,
                "purchase": getattr(record, 'purchase', False),
                "price": total_price,
                "created_at": record.created_at,
                "prescriptions": prescription_data
            })

        return {
            "status": "success",
            "data": result_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/medical-records", response_model=schemas.MedicalRecordResponse,
          summary=endpoint_descriptions["create_medical_record"]["summary"],
          description=endpoint_descriptions["create_medical_record"]["description"],
          response_description=endpoint_descriptions["create_medical_record"]["response_description"],
          tags=["진료"]
          )
async def create_medical_record(record: schemas.MedicalRecordCreate, db: Session = Depends(get_db)):
    try:
        # 환자의 가장 최근 접수 기록 찾기
        latest_checkin = (
            db.query(models.CheckIn)
            .filter(models.CheckIn.patient_id == record.patient_id)
            .order_by(models.CheckIn.check_in_time.desc())
            .first()
        )

        if not latest_checkin:
            raise HTTPException(status_code=404, detail="해당 환자의 접수 기록을 찾을 수 없습니다")

        # 기본 진찰료 설정
        total_price = BASE_CONSULTATION_FEE

        # 약품 가격 미리 계산
        for prescription in record.prescriptions:
            medicine_price = MEDICINE_PRICES.get(prescription.medicine_name, 0)
            total_price += medicine_price

        # 먼저 진료기록 생성
        db_record = models.MedicalRecord(
            patient_id=record.patient_id,
            checkin_id=latest_checkin.id,
            diagnosis=record.diagnosis,
            comment=record.comment,
            purchase=False,
            price=total_price,
            created_at=datetime.now()
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)

        # 그 다음 처방기록 생성
        prescriptions = []
        for prescription in record.prescriptions:
            medicine_price = MEDICINE_PRICES.get(prescription.medicine_name, 0)
            db_prescription = models.Prescription(
                medical_record_id=db_record.id,  # 이제 db_record가 존재함
                medicine_name=prescription.medicine_name,
                dosage=prescription.dosage,
                usage_instructions=prescription.usage_instructions,
                price=medicine_price,
                created_at=datetime.now()
            )
            db.add(db_prescription)
            prescriptions.append(db_prescription)
        
        db.commit()

        return {
            "id": db_record.id,
            "patient_id": record.patient_id,
            "checkin_id": latest_checkin.id,
            "patient_name": latest_checkin.patient.name,
            "patient_phone": latest_checkin.patient.phone,
            "diagnosis": db_record.diagnosis,
            "comment": db_record.comment,
            "purchase": db_record.purchase,
            "price": db_record.price,
            "created_at": db_record.created_at,
            "prescriptions": [
                {
                    "id": p.id,
                    "medicine_name": p.medicine_name,
                    "dosage": p.dosage,
                    "usage_instructions": p.usage_instructions,
                    "price": p.price,
                    "created_at": p.created_at
                } for p in prescriptions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/prescriptions/{medical_record_id}",
         summary=endpoint_descriptions["get_prescriptions"]["summary"],
         description=endpoint_descriptions["get_prescriptions"]["description"],
         response_description=endpoint_descriptions["get_prescriptions"]["response_description"],
         tags=["진료"]
         )
async def get_prescriptions_by_medical_record(medical_record_id: int, db: Session = Depends(get_db)):
    try:
        prescriptions = (
            db.query(models.Prescription)
            .filter(models.Prescription.medical_record_id == medical_record_id)
            .all()
        )

        if not prescriptions:
            raise HTTPException(status_code=404, detail="처방기록을 찾을 수 없습니다")

        return {
            "status": "success",
            "data": [
                {
                    "id": prescription.id,
                    "medicine_name": prescription.medicine_name,
                    "dosage": prescription.dosage,
                    "usage_instructions": prescription.usage_instructions,
                    "created_at": prescription.created_at
                } for prescription in prescriptions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))