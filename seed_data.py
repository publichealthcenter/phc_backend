from datetime import datetime, timedelta
from database import SessionLocal
import models
import random

# 더미 데이터 생성을 위한 샘플 데이터
sample_names = [
    "김영희", "이철수", "박민지", "정수민", "강지훈",
    "윤서연", "임재현", "한미영", "송태호", "조은지"
]

sample_phones = [
    "010-1234-5678", "010-2345-6789", "010-3456-7890",
    "010-4567-8901", "010-5678-9012", "010-6789-0123",
    "010-7890-1234", "010-8901-2345", "010-9012-3456",
    "010-0123-4567"
]

sample_diagnoses = [
    "감기", "고혈압", "당뇨", "관절염", "위염",
    "두통", "요통", "알레르기", "피부염", "소화불량"
]

sample_medicines = [
    "타이레놀", "아스피린", "이부프로펜", "메트포민",
    "암로디핀", "오메프라졸", "디클로페낙", "세티리진"
]

def create_dummy_data():
    db = SessionLocal()
    try:
        for i in range(10):
            patient = models.Patient(
                name=sample_names[i],
                phone=sample_phones[i],
                created_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            db.add(patient)
            db.commit()
            db.refresh(patient)


            for _ in range(random.randint(1, 3)):
                checkin_time = datetime.now() - timedelta(days=random.randint(1, 15))
                checkin = models.CheckIn(
                    patient_id=patient.id,
                    check_in_time=checkin_time
                )
                db.add(checkin)
                db.commit()
                db.refresh(checkin)


                medical_record = models.MedicalRecord(
                    patient_id=patient.id,
                    checkin_id=checkin.id,
                    diagnosis=random.choice(sample_diagnoses),
                    comment=f"환자 상태: {'양호' if random.random() > 0.5 else '요관찰'}",
                    purchase=False,  # Add this line
                    created_at=checkin_time + timedelta(minutes=random.randint(30, 120))
                )
                db.add(medical_record)
                db.commit()
                db.refresh(medical_record)


                for _ in range(random.randint(1, 3)):
                    prescription = models.Prescription(
                        medical_record_id=medical_record.id,
                        medicine_name=random.choice(sample_medicines),
                        dosage=f"{random.choice([100, 200, 300, 500])}mg",
                        usage_instructions=f"1일 {random.randint(1, 3)}회 식후 {random.randint(20, 40)}분",
                        created_at=medical_record.created_at
                    )
                    db.add(prescription)

            for _ in range(random.randint(0, 2)):
                current_time = datetime.now() - timedelta(days=random.randint(1, 7))
                reservation = models.Reservation(
                    patient_id=patient.id,
                    current_time=current_time,
                    reservation_time=current_time + timedelta(days=random.randint(1, 14))
                )
                db.add(reservation)

        db.commit()
        print("더미 데이터가 성공적으로 생성되었습니다.")

    except Exception as e:
        print(f"데이터 생성 중 오류 발생: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_dummy_data()