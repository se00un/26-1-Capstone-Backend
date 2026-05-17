import json
from sqlalchemy.orm import Session
from fastapi import HTTPException
from openai import OpenAI
import os
from dotenv import load_dotenv


from app.models import TripReport, Trip, Expense, Route, RoutePlace, TripMember

load_dotenv()
client = OpenAI(api_key=os.getenv("REPORT_OPENAI_API_KEY"))


def aggregate_trip_data(trip_id: int, current_user_id: int, db: Session) -> dict:

    trip = db.query(Trip).filter(Trip.id == trip_id).first()

    # shared expenses — 카테고리별 합계
    shared_expenses = (
        db.query(Expense)
        .filter(
            Expense.trip_id == trip_id,
            Expense.expense_type == "shared"
        )
        .all()
    )
    shared_by_category = {}
    for e in shared_expenses:
        shared_by_category[e.category] = (
            shared_by_category.get(e.category, 0) + float(e.amount_krw or 0)
        )

    # personal expenses — 본인 것만
    personal_expenses = (
        db.query(Expense)
        .filter(
            Expense.trip_id == trip_id,
            Expense.expense_type == "personal",
            Expense.created_by == current_user_id,
        )
        .all()
    )
    personal_by_category = {}
    for e in personal_expenses:
        personal_by_category[e.category] = (
            personal_by_category.get(e.category, 0) + float(e.amount_krw or 0)
        )

    # 방문 장소 목록
    routes = db.query(Route).filter(Route.trip_id == trip_id).all()
    visited_places = []
    for route in routes:
        places = (
            db.query(RoutePlace)
            .filter(RoutePlace.route_id == route.id)
            .order_by(RoutePlace.visit_order)
            .all()
        )
        for p in places:
            visited_places.append({
                "place_name": p.place_name,
                "city": p.city,
                "country": p.country,
                "place_type": p.place_type,
            })

    return {
        "trip_title": trip.title,
        "start_date": str(trip.start_date),
        "end_date": str(trip.end_date),
        "duration_days": (trip.end_date - trip.start_date).days + 1,
        "shared_expenses_by_category": shared_by_category,
        "personal_expenses_by_category": personal_by_category,
        "total_shared_krw": sum(shared_by_category.values()),
        "total_personal_krw": sum(personal_by_category.values()),
        "visited_places": visited_places,
    }


def build_prompt(data: dict) -> str:

    prompt = f"""
당신은 여행 분석 전문가입니다. 아래 여행 데이터를 바탕으로 여행 리포트를 작성해주세요.

## 여행 정보
- 여행명: {data['trip_title']}
- 기간: {data['start_date']} ~ {data['end_date']} ({data['duration_days']}일)

## 공동 소비 내역 (KRW 기준)
{json.dumps(data['shared_expenses_by_category'], ensure_ascii=False, indent=2)}
공동 소비 합계: {data['total_shared_krw']:,.0f}원

## 개인 소비 내역 (KRW 기준)
{json.dumps(data['personal_expenses_by_category'], ensure_ascii=False, indent=2)}
개인 소비 합계: {data['total_personal_krw']:,.0f}원

## 방문 장소 목록
{json.dumps(data['visited_places'], ensure_ascii=False, indent=2)}

---

위 데이터를 바탕으로 아래 JSON 형식으로 정확하게 응답해주세요.
다른 텍스트 없이 JSON만 반환해주세요.

{{
  "trip_summary": "이번 여행 전체 요약 (2~3문장)",
  "spending_analysis": "소비 패턴 분석. 공동/개인 소비를 구분하여 어떤 카테고리에 많이 썼는지 분석 (2~3문장)",
  "trip_vibe": "이번 여행의 분위기와 스타일 (1~2문장)",
  "highlight_places": "인상적인 장소 유형 또는 특징 (1~2문장)",
  "next_style": "다음 여행 스타일 추천 (1문장)",
  "recommendations": [
    {{
      "destination": "추천 목적지명",
      "country": "국가명",
      "is_overseas": true or false,
      "reason": "이번 여행 데이터 기반으로 구체적인 추천 이유"
    }},
    {{ ... }},
    {{ ... }}
  ]
}}

recommendations는 이번 여행 스타일과 소비 패턴을 분석하여 잘 맞는 곳으로 총 3곳 추천해주세요.
"""
    return prompt.strip()


def call_llm(prompt: str) -> dict:
    """OpenAI API를 호출하고 JSON 결과를 반환합니다."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "당신은 여행 분석 전문가입니다. 반드시 JSON 형식으로만 응답하세요.",
            },
            {
                "role": "user",
                "content": prompt
            },
        ],
        temperature=0.7,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    return json.loads(raw)


def save_report(
    trip_id: int,
    current_user_id: int,
    llm_result: dict,
    db: Session,
) -> TripReport:

    report_text = f"""[여행 요약]
{llm_result['trip_summary']}

[소비 패턴 분석]
{llm_result['spending_analysis']}

[여행 분위기]
{llm_result['trip_vibe']}

[인상적인 장소]
{llm_result['highlight_places']}

[다음 여행 스타일]
{llm_result['next_style']}""".strip()

    summary_json = {
        "trip_summary": llm_result["trip_summary"],
        "spending_analysis": llm_result["spending_analysis"],
        "trip_vibe": llm_result["trip_vibe"],
        "highlight_places": llm_result["highlight_places"],
        "next_style": llm_result["next_style"],
    }

    recommendation_text = "\n".join([
        f"- {r['destination']} ({r['country']}): {r['reason']}"
        for r in llm_result["recommendations"]
    ])

    report = TripReport(
        trip_id=trip_id,
        generated_by=current_user_id,
        report_text=report_text,
        summary_json=summary_json,
        recommendation_text=recommendation_text,
        recommended_destinations_json=llm_result["recommendations"],
    )

    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def generate_trip_report(
    trip_id: int,
    current_user_id: int,
    db: Session,
) -> TripReport:

    # 재생성 방지
    existing = db.query(TripReport).filter(TripReport.trip_id == trip_id).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Trip report already exists for this trip.",
        )

    data = aggregate_trip_data(trip_id, current_user_id, db)
    prompt = build_prompt(data)
    llm_result = call_llm(prompt)
    report = save_report(trip_id, current_user_id, llm_result, db)

    return report