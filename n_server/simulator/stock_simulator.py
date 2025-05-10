from collections import deque
import numpy as np
from zoneinfo import ZoneInfo
import datetime

# 전역 변수
SIGMA = 0.015     # 변동성 (낮출수록 부드러움, 현실적)
MU = 0.00015      # 기대 수익률 (아주 약한 우상향)
DT = 1/3600       # 시간 간격 (1초 = 1/3600시간)
company_base_means = {}

hour_count = 0
sec_count = 0
def brownian_motion(S0, company_name=None):
    global MU, SIGMA, hour_count, sec_count, company_base_means

    S = S0

    # 초기 평균 등록
    if company_name:
        if company_name not in company_base_means:
            company_base_means[company_name] = S0
    else:
        if 'default' not in company_base_means:
            company_base_means['default'] = S0

    # 변동성 조정: 급격한 점프를 줄이기 위해 dW를 제한
    dW = np.clip(np.random.normal(0, np.sqrt(DT)), -0.03, 0.03)
    dS = MU * S * DT + SIGMA * S * dW
    S += dS

    # 급등락 이벤트: 확률 줄이고 강도도 더 낮춤
    if np.random.rand() < 0.0005:  # 0.05% 확률
        event_type = np.random.choice(["good", "bad"])
        if event_type == "good":
            S *= np.random.uniform(1.01, 1.03)  # 완만한 급등
            print(f"{company_name} 🚀 완만한 급등 이벤트 발생!")
        else:
            S *= np.random.uniform(0.97, 0.99)  # 완만한 급락
            print(f"{company_name} 💥 완만한 급락 이벤트 발생!")

    # 가격 제한 (20~500)
    S = max(S, 20)
    S = min(S, 500)

    # 시간 카운트 및 장기 변화
    sec_count += 1
    if sec_count % 3600 == 0:
        hour_count += 1
        sec_count = 0
        if hour_count % 8 == 0:
            long_term_shift = np.random.uniform(-0.00005, 0.00005)
            MU += long_term_shift
            print(f"🌍 장기 추세 변화: MU={MU:.6f}")

            shift_ratio = np.random.uniform(-0.001, 0.001)
            if company_name:
                company_base_means[company_name] *= (1 + shift_ratio)
            else:
                company_base_means['default'] *= (1 + shift_ratio)
            print(f"{company_name or 'default'} 평균 이동: {shift_ratio*100:.2f}% 적용")

    print(f"{company_name or 'default'} 가격: {round(S, 2)}")
    return round(S, 2)
