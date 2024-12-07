from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    # 관계 설정
    checkins = relationship("CheckIn", back_populates="patient")
    reservations = relationship("Reservation", back_populates="patient")
    medical_records = relationship("MedicalRecord", back_populates="patient")

class CheckIn(Base):
    __tablename__ = "checkins"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    check_in_time = Column(DateTime, nullable=False)

    # 관계 설정
    patient = relationship("Patient", back_populates="checkins")
    medical_records = relationship("MedicalRecord", back_populates="checkin")

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    current_time = Column(DateTime, nullable=False)
    reservation_time = Column(DateTime, nullable=False)

    # 관계 설정
    patient = relationship("Patient", back_populates="reservations")

class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    checkin_id = Column(Integer, ForeignKey("checkins.id"), nullable=False)
    diagnosis = Column(String, nullable=False)
    comment = Column(String, nullable=True)
    purchase = Column(Boolean, default=False, nullable=False)
    price = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    # 관계 설정
    patient = relationship("Patient", back_populates="medical_records")
    checkin = relationship("CheckIn", back_populates="medical_records")
    prescriptions = relationship("Prescription", back_populates="medical_record")

class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    medical_record_id = Column(Integer, ForeignKey("medical_records.id"))
    medicine_name = Column(String)
    dosage = Column(String)
    usage_instructions = Column(String)
    price = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)

    medical_record = relationship("MedicalRecord", back_populates="prescriptions")