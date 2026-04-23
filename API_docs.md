# Trip-log: REST API Specification

본 문서는 **Trip-log** 서비스의 백엔드(FastAPI) REST API 요청(Request) 및 응답(Response) 바디에 대한 상세 명세서입니다. 

---

## 0. Authentication (Google OAuth 2.0)

### `POST /api/auth/google`
- **Description**: 구글 로그인 (ID Token 검증 후 자체 JWT 발급 및 유저 생성)
- **Request Body (application/json)**
  ```json
  {
    "id_token": "string (Google에서 발급받은 JWT ID Token)"
  }
  ```
- **Response Body (200 OK)**
  ```json
  {
    "access_token": "string",
    "refresh_token": "string",
    "user": { #USER table과 동일
      "id": 1,
      "email": "user@gmail.com",
      "nickname": "string",
      "provider": "google", # fixed
      "provider_id": "string",
      "profile_image_url": "https://...",
      "created_at": "2024-01-01T12:00:00Z"
    }
  }
  ```

### `POST /api/auth/refresh`
- **Description**: 만료된 Access Token 재발급
- **Request Body (application/json)**
  ```json
  {
    "refresh_token": "string"
  }
  ```
- **Response Body (200 OK)**
  ```json
  {
    "access_token": "string",
    "token_type": "bearer"
  }
  ```

### `GET /api/users/me`
- **Description**: 현재 로그인된 사용자 정보 및 프로필 조회
- **Request Body**: None
- **Response Body (200 OK)**
  ```json
  { # User table과 동일
    "id": 1,
    "email": "user@gmail.com",
    "nickname": "string",
    "provider": "google", # fixed
    "provider_id": "string",
    "profile_image_url": "https://...",
    "created_at": "2024-01-01T12:00:00Z"
  }
  ```

---

## 🌎 1. Trips & Membership (여정 관리)

### `POST /api/trips`
- **Description**: 새로운 여행 생성
- **Request Body (application/json)**
  ```json
  {
    "title": "다같이 제주도 여행",
    "start_date": "2024-05-01",
    "end_date": "2024-05-05",
    "is_group_trip": true
  }
  ```
- **Response Body (201 Created)**
  ```json
  {
    "id": 101,
    "owner_id": 1,
    "title": "다같이 제주도 여행",
    "start_date": "2024-05-01",
    "end_date": "2024-05-05",
    "is_group_trip": true,
    "status": "ongoing",
    "created_at": "2024-04-10T10:00:00Z"
  }
  ```

### `GET /api/trips/my`
- **Description**: 내가 참여 중인 전체 여행 목록 조회 (3D Globe 핀용)
- **Request Body**: None
- **Response Body (200 OK)**
  ```json
  [
    {
    "id": 101,
    "owner_id": 1,
    "title": "다같이 제주도 여행",
    "start_date": "2024-05-01",
    "end_date": "2024-05-05",
    "is_group_trip": true,
    "status": "ongoing",
    "created_at": "2024-04-10T10:00:00Z",
    "role": "owner" # "owner", "editor"
    },
    {
      ...
    }
  ]
  ```

### `POST /api/trips/{trip_id}/invites`
- **Description**: 특정 여행의 초대 코드 생성 (Owner/Editor 전용)
- **Request Body (application/json, optional)**
  ```json
  {
    "trip_id": 101,
    "expires_at": "2024-04-11T10:00:00Z"
  }
  ```
- **Response Body (201 Created)**
  ```json
  {
    "id": 1, #invitation id (PK)
    "trip_id": 101,
    "invite_code": "ABC123DEF",
    "invited_by": 1,
    "status": "pending",
    "expires_at": "2024-04-11T10:00:00Z",
    "created_at": "2024-04-10T10:00:00Z"
  }
  ```

### `POST /api/invites/{invite_code}/accept`
- **Description**: 초대 코드를 사용하여 여행 그룹에 참여
- **Request Body**: None
- **Response Body (200 OK)**
  ```json
  { 
    # trip_members table
    "trip_id": 101,
    "user_id": 2,
    "role": "editor",
    "joined_at": "2024-04-10T10:30:00Z"
  }
  ```

---

## 💸 2. Budget & Expense (예산 및 지출)

### `PUT /api/budget/{trip_id}`
- **Description**: 총 예산 및 카테고리별 예산 설정 (Upsert)
- **Request Body (application/json)**
  ```json
  {
    # budget table
    "budgets":  [
      {
        "category": "food",
        "amount": 100000.0,
        "currency": "KRW",
        "amount_krw": 100000.0
      },
      {
        ... 
      }
    ]
  }
  ```
- **Response Body (200 OK)**
  `Request Body와 동일 + id, trip_id, updated_at 포플릿`

### `POST /api/expenses/{trip_id}`
- **Description**: 지출 내역 입력 
- **Request Body (application/json)**
  ```json
  {
    "expense_type": "shared", // "shared" or "personal"
    "title": "저녁 식사 (흑돼지)",
    "category": "food",
    "amount_original": 80000.0,
    "currency": "KRW",
    "amount_krw": 80000.0,
    "expense_date": "2024-05-01",
    "memo": "맛있게 먹음",
    "receipt_id": null
  }
  ```
- **Response Body (201 Created)**
  ```json
  {
    "id": 501,
    "trip_id": 101,
    "created_by": 1,
    "expense_type": "shared",
    "title": "저녁 식사 (흑돼지)",
    ...Request Fields,
    "created_at": "2024-05-01T20:00:00Z"
  }
  ```

### `GET /api/expenses/{trip_id}`
- **Description**: 지출 목록 조회 (Shared는 전체, Personal은 본인 것만)
- **Request Body**: None
- **Response Body (200 OK)**
  ```json
  [
    {
       "id": 501,
       "expense_type": "shared",
       "title": "저녁 식사 (흑돼지)",
       "category": "food",
       "amount_original": 80000.0,
       "currency": "KRW",
       "exchange_rate": 1.0,
       "amount_krw": 80000.0,
       "expense_date": "2024-05-01",
       "memo": "맛있게 먹음",
       "created_by": 1
    }
  ]
  ```

### `GET /api/budget/{trip_id}/summary`
- **Description**: 예산 위험도(Burn Rate) 및 통계 조회, 호출 시 backend에서 계산 (budget & expense table)
- **Request Body**: None
- **Response Body (200 OK)**
  ```json
  {
  "total_budget_krw": 1000000,
  "total_expense_krw": 450000,
  "burn_rate": 0.92,
  "risk_status": "warning",
  "category_stats": {
    "food": {"expense": 150000, "budget": 400000 },
    "transport": { "expense": 200000, "budget": 200000 }
    } 
  }
  ```

### `POST /api/expenses/{expense_id}/split`
- **Description**: 특정 Shared Expense에 대한 1/N 정산 금액 계산 추가
- **Request Body (application/json)**
  ```json
  {
    "user_ids": [1, 2, 3]
  }
  ```
- **Response Body (201 Created)**
  ```json
  {
    "id": 501, # expense_split id
    "expense_id": 501,
    "total_amount_krw": 45000,
    "splits": [
      {
        "user_id": 1,
        "nickname": "정우",
        "split_amount": 15000
      },
      {
        "user_id": 2,
        "nickname": "지수",
        "split_amount": 15000
      },
      {
        "user_id": 3,
        "nickname": "현우",
        "split_amount": 15000
      }
    ],
    "created_at": "2026-03-31T20:05:00Z"
  }
  ```

---

## 📸 3. AI OCR Pipeline (영수증 자동화)

### `POST /api/receipts/{trip_id}/upload`
- **Description**: 영수증 이미지 업로드 및 OCR 분석 시작
- **Request Body (multipart/form-data)**
  - `file`: image/jpeg or image/png
- **Response Body (202 Accepted)**
  ```json
  {
    "id": 1001, # receipt id
    "trip_id": 101,
    "image_url": "https://bucket.s3.../receipt.jpg"
  }
  ```

### `GET /api/receipts/{trip_id}`
- **Description**: OCR 분석 결과(JSON) 조회 (사용자 검수 단계)
- **Request Body**: None
- **Response Body (200 OK)**
  ```json
  {
    "id": 1001, # receipt id
    "status": "completed",
    "image_url": "https://...",
    "parsed_json": 
      {
        "amount_original": 12000, 
        "currency": "KRW", 
        "category": "cafe", 
        "expense_date": "2024-05-02"
      },
    "raw_ocr_text": "...",
    "created_at": "2024-05-02T10:00:00Z"
  }
  ```

### `POST /api/receipts/{receipt_id}/confirm-receipt`
- **Description**: 사용자가 업로드하여 파싱된 OCR 데이터를 Expense로 최종 확정
- **Request Body (application/json)**
  - `POST /api/expenses/{trip_id}` 와 동일한 Request Body 구조 사용 (수정된 값 포함)
  ```json
  {
      "expense_type": "shared",
      "title": "저녁 식사 (흑돼지)",
      "category": "food",
      "amount_original": 80000.0,
      "currency": "KRW",
      "amount_krw": 80000.0,
      "expense_date": "2024-05-01",
      "memo": "맛있게 먹음",
      "created_by": 1
  }
  ```
- **Response Body (201 Created)**
  - `EXPENSES` 생성 응답과 동일 (`receipt_id`가 매핑된 형태)
  ```json
  {
    "id": 501,
    "trip_id": 101,
    "created_by": 1,
    "expense_type": "shared",
    "title": "저녁 식사 (흑돼지)",
    ...Request Fields,
    "receipt_id": 1001,
    "created_at": "2024-05-01T20:00:00Z"
  }
  ```

---

## 📍 4. Routes & Votes (동선 및 협업)

### `GET /api/routes/{trip_id}`
- **Description**: 여행 경로(Routes) 및 방문 장소 목록 조회
- **Request Body**: None
- **Response Body (200 OK)**
  ```json
  [
    {
      "id": 101, # route_id
      "trip_id": 101,
      "title": "1일차", # route_title
      "places": [
        { # route_places 테이블
          "id": 201, #place_id
          "place_name": "제주공항",
          "country": "KR",
          "city": "제주시",
          "address": "제주 제주시 공항로 2",
          "latitude": 33.5104,
          "longitude": 126.4913,
          "place_type": "Airport",
          "visit_order": 1,
          "memo": "출발지",
          "visited_at": "2026-03-31T10:00:00Z"
        },
        {
          ...
        }
      ]
    }
  ]
  ```

### `POST /api/routes/{route_id}/places`
- **Description**: 새로운 방문 장소 추가 (특정 Route에 종속)
- **Request Body (application/json)**
  ```json
  {
    "place_name": "올레 국수",
    "country": "KR",
    "city": "제주시",
    "address": "제주 제주시 귀아랑길 24",
    "latitude": 33.4939, 
    "longitude": 126.4967, 
    "place_type": "Restaurant",
    "visit_order": 2,
    "memo": "고기국수 맛집"
  }
  ```
- **Response Body (201 Created)**
  ```json
  {
    "id": 202, #place_id
    "route_id": 10,
    "place_name": "올레 국수",
    ...Request Fields,
    "visited_at": null
  }
  ```

### `PATCH /api/routes/{routeid}/order`
- **Description**: 방문 순서(visit_order) 재배치 
- **Request Body (application/json)**
  ```json
  {
    "orders": [
      { "place_id": 201, "visit_order": 2 },
      { "place_id": 202, "visit_order": 1 }
    ]
  }
  ```
- **Response Body (200 OK)**
  ```json
  {
    "message": "Visit order updated successfully."
  }
  ```

### `DELETE /api/routes/{route_id}`
- **Description**: 특정 여행 경로(Route) 삭제
- **Request Body**: None
- **Response Body (200 OK)**
  ```json
  {
    "message": "Route deleted successfully."
  }
  ```

### `POST /api/votes/{trip_id}`
- **Description**: 새로운 장소/메뉴 투표 생성
- **Request Body (application/json)**
  ```json
  {
    "title": "오늘 저녁 뭐먹지?",
    "description": "흑돼지 vs 회",
    "option_text": [
      "흑돼지 (칠돈가)",
      "방어회 (동문시장)"
    ]
  }
  ```
- **Response Body (201 Created)**
  ```json
  {
    "id": 1, #vote_options id
    "trip_id": 101,
    "created_by": 1,
    "title": "오늘 저녁 뭐먹지?",
    "description": "흑돼지 vs 회",
    "status": "active",
    "option_text": [
      { "vote_id": 11, "option_text": "흑돼지 (칠돈가)" },
      { "vote_id": 12, "option_text": "방어회 (동문시장)" }
    ],
    "created_at": "2026-03-31T20:05:00Z"
  }
  ```

### `POST /api/votes/{vote_id}/responses`
- **Description**: 투표 참여 (선택지 클릭) 
- **Request Body (application/json)**
  ```json
  {
    "option_id": 11 #vote options id
  }
  ```
- **Response Body (201 Created)**
  ```json
  {
    "id": 50, #response id
    "vote_id": 1,
    "option_id": 11,
    "user_id": 2,
    "created_at": "..."
  }
  ```

### `GET /api/votes/{vote_id}/results`
- **Description**: 투표 결과 조회
- **Request Body**: None
- **Response Body (200 OK)**
  ```json
  {
    "id": 1, # vote id
    "title": "오늘 저녁 뭐먹지?",
    "description": "흑돼지 vs 회",
    "status": "closed",
    "created_by": 1,
    "options": [
      {
        "id": 11, # option id
        "option_text": "흑돼지 (칠돈가)",
        "vote_count": 10
      },
      {
        "id": 12,
        "option_text": "방어회 (동문시장)",
        "vote_count": 5
      }
    ]
  }
  ```

---

## 📊 5. AI Insight Reports (리포트)

### `POST /api/reports/{trip_id}/generate`
- **Description**: [Trip-level] 이번 여행 요약 및 소비 분석 리포트 생성 (SQL-RAG)
- **Request Body**: None 
- **Response Body (200 OK)**
  ```json
  {
    "id": 5,
    "trip_id": 101,
    "generated_by": 1,
    "report_text": "이번 제주도 여행에서는 식비 비중이 예산보다 높았습니다...",
    "summary_json": {
        "top_category": "food", 
        "total_spent": 450000
    },
    "created_at": "2024-05-06T10:00:00Z",
    "recommendation_text": "과거 여행 데이터를 분석한 결과, 다음 여행지로는 오사카를 추천합니다...",
    "recommended_destinations_json": [
        "Osaka, Japan", 
        "Fukuoka, Japan"
    ] 
  }
  ```
