from typing import Dict

tags_metadata = [
    {
        "name": "접수",
        "description": "환자 접수 관련 API",
    },
    {
        "name": "예약",
        "description": "환자 예약 관련 API",
    },
    {
        "name": "진료",
        "description": "진료 및 처방 관련 API",
    }
]

api_metadata = {
    "title": "보건소 키오스크 시스템 API",
    "description": "환자 접수, 예약, 진료 기록을 관리하는 API",
    "version": "1.0.0",
    "openapi_tags": tags_metadata
}

examples = {
    "checkin": {
        "request": {
            "name": "홍길동",
            "phone": "010-1234-5678",
            "check_in_time": "2024-03-20T14:30:00"
        }
    },
    "reservation": {
        "request": {
            "name": "홍길동",
            "phone": "010-1234-5678",
            "reservation_time": "2024-03-21T10:00:00"
        }
    },
    "medical_record": {
        "request": {
            "patient_id": 1,
            "diagnosis": "감기",
            "comment": "발열 있음",
            "prescriptions": [
                {
                    "medicine_name": "타이레놀",
                    "dosage": "500mg",
                    "usage_instructions": "1일 3회 식후 30분"
                }
            ]
        }
    }
}

endpoint_descriptions = {
    # 접수 관련
    "checkin": {
        "summary": "환자 접수하기",
        "description": "새로운 환자를 접수합니다. 환자가 존재하지 않으면 새로 생성합니다.",
        "response_description": "생성된 접수 정보를 반환합니다.",
    },
    "get_checkins": {
        "summary": "전체 접수 목록 조회",
        "description": "모든 환자의 접수 기록을 조회합니다.",
        "response_description": "접수 목록을 반환합니다.",
    },

    # 예약 관련
    "create_reservation": {
        "summary": "예약하기",
        "description": "새로운 예약을 생성합니다. 환자가 존재하지 않으면 새로 생성합니다.",
        "response_description": "생성된 예약 정보를 반환합니다.",
    },
    "get_reservation": {
        "summary": "예약 조회",
        "description": "환자의 전화번호로 예약 정보를 조회합니다.",
        "response_description": "환자의 예약 정보를 반환합니다.",
    },

    # 진료 관련
    "create_medical_record": {
        "summary": "진료 기록 생성",
        "description": "환자의 진료 기록과 처방전을 생성합니다.",
        "response_description": "생성된 진료 기록과 처방전 정보를 반환합니다.",
    },
    "get_medical_records_by_patient_id": {
        "summary": "환자 ID로 진료기록 조회",
        "description": "환자 ID를 사용하여 진료기록을 조회합니다.",
        "response_description": "환자의 진료기록 목록을 반환합니다.",
    },
    "get_medical_records_by_phone": {
        "summary": "전화번호로 진료기록 조회",
        "description": "환자의 전화번호로 진료기록을 조회합니다.",
        "response_description": "환자의 진료기록 목록을 반환합니다.",
    },
    "get_prescriptions": {
        "summary": "처방전 조회",
        "description": "진료기록 ID로 처방전을 조회합니다.",
        "response_description": "처방전 목록을 반환합니다.",
    }
}

parameter_descriptions = {
    "phone": "환자 전화번호 (예: 010-1234-5678)",
    "patient_id": "환자 ID",
    "medical_record_id": "진료기록 ID",
    "name": "환자 이름",
    "check_in_time": "접수 시간",
    "reservation_time": "예약 시간",
    "diagnosis": "진단 내용",
    "comment": "특이사항 (선택사항)",
    "medicine_name": "약품명",
    "dosage": "용량",
    "usage_instructions": "복용 방법"
}