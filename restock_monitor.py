#!/usr/bin/env python3
"""
GuitarNet - Quad Cortex Mini 재입고 감시기 (알림 전용)

- 상품 페이지를 긁어서 'SOLD OUT'(품절 버튼) 문자열이 사라지면 = 재입고로 판단
- 재입고 시 Telegram 으로 푸시 알림
- 표준 라이브러리만 사용 (pip 설치 불필요)

⚠️ 이 스크립트는 '알림'만 보냄. 자동 구매/결제는 하지 않음(그건 직접 눌러서 사).
"""

import os
import sys
import urllib.request
import urllib.parse

# ─────────────────────────────────────────────────────────────
# 1) 설정
# ─────────────────────────────────────────────────────────────

# ★ 주소창의 '전체' URL로 교체할 것 (스크린샷 URL이 category/666 뒤로 잘려 있음)
PRODUCT_URL = "https://guitarnet.cafe24.com/product/quad-cortex-mini/4612/category/666/display/1/"

# 품절 상태를 나타내는 마커. 'SOLD OUT'이 가장 신뢰도 높음(그 버튼에만 등장).
# 오탐이 나면 아래 리스트를 좁히거나(예: ["SOLD OUT"] 만) 늘려서 조정.
SOLDOUT_MARKERS = ["SOLD OUT"]

# Telegram (환경변수 또는 GitHub Secrets 로 주입)
TG_TOKEN = os.environ.get("TG_TOKEN", "8899644722:AAFLZEUbhMnwrw8cMYJU7gINoNuBvSrtCVs")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID", "6066433342")
# ⚠️ 토큰이 파일에 박혀 있으니, GitHub 등 '공개' 레포에 올릴 거면 위 두 줄의 기본값을 지우고
#    반드시 Secrets/환경변수로만 넣을 것.

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36")


# ─────────────────────────────────────────────────────────────
# 2) 동작
# ─────────────────────────────────────────────────────────────

def fetch(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Accept-Language": "ko-KR,ko;q=0.9"},
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", "ignore")


def is_in_stock(html: str) -> bool:
    """품절 마커가 하나도 없으면 재입고로 판단."""
    low = html.lower()
    return not any(m.lower() in low for m in SOLDOUT_MARKERS)


def notify(msg: str) -> None:
    if not (TG_TOKEN and TG_CHAT_ID):
        print("[텔레그램 미설정] 알림 내용:", msg)
        return
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": TG_CHAT_ID, "text": msg}).encode()
    urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=20).read()


def main() -> None:
    try:
        html = fetch(PRODUCT_URL)
    except Exception as e:
        # 일시적 네트워크 오류로 알림 스팸이 나지 않게 조용히 종료
        print("fetch 실패(무시):", e)
        sys.exit(0)

    if is_in_stock(html):
        notify(f"🎸 재입고! Quad Cortex Mini 구매 가능\n{PRODUCT_URL}")
        print("IN STOCK ▶ 알림 전송")
    else:
        print("still sold out")


if __name__ == "__main__":
    main()
