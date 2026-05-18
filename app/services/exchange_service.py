import requests
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def get_exchange_rate(date_str: str, from_currency: str, to_currency: str = "KRW") -> tuple[float, bool]:
    """
    환율 Fallback 로직 적용
    1순위: 해당 날짜 환율
    2순위: 최근 7일 이내 환율
    3순위: 1.0 fallback + exchange_rate_fallback: true
    
    Returns:
        (rate, is_fallback)
    """
    from_currency = from_currency.lower()
    to_currency = to_currency.lower()
    
    if from_currency == to_currency:
        return 1.0, False

    base_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    
    # 1순위 ~ 2순위 (최대 7일 전까지 탐색)
    for i in range(8):
        target_date = base_date - timedelta(days=i)
        date_formatted = target_date.strftime("%Y-%m-%d")
        
        url = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{date_formatted}/v1/currencies/{from_currency}.json"
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                data = response.json()
                if from_currency in data and to_currency in data[from_currency]:
                    return float(data[from_currency][to_currency]), False
        except requests.RequestException:
            pass
            
    # 3순위 (fallback)
    logger.warning(f"Could not fetch exchange rate for {from_currency} to {to_currency} around {date_str}. Using fallback 1.0.")
    return 1.0, True
