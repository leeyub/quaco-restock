#!/usr/bin/env python3
"""
GuitarNet - Quad Cortex Mini 재입고 감시기 v2

구조:
- GitHub Actions 가 30분마다 이 스크립트를 실행
- 실행되면 먼저 '생존신고'를 텔레그램으로 1번 보냄 (무음 알림)
- 그 후 약 28분 동안 60초 간격으로 페이지를 확인
- 'SOLD OUT' 문구가 사라지면 = 재입고 → 즉시 소리나는 알림 보내고 종료

⚠️ 알림만 보냄. 자동 구매는 하지 않음.
"""

import os
import sys
import time
import urllib.request
import urllib.parse

# ── 설정 ──────────────────────────────────────────────
PRODUCT_URL = "https://guitarnet.cafe24.com/product/quad-cortex-mini/4612/category/666/display/1/"
SOLDOUT_MARKERS = ["SOLD OUT"]

CHECK_INTERVAL_SEC = 30      # 30초마다 확인
SESSION_MINUTES = 28         # 한 세션 약 28분 (30분 주기와 맞물리게)

TG_TOKEN = os.environ.get("TG_TOKEN", "")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID", "6066433342")

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36")


# ── 동작 ──────────────────────────────────────────────
def fetch(url: str) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": UA, "Accept-Language": "ko-KR,ko;q=0.9"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", "ignore")


def is_in_stock(html: str) -> bool:
    low = html.lower()
    return not any(m.lower() in low for m in SOLDOUT_MARKERS)


def send(msg: str, silent: bool = False) -> None:
    """silent=True 면 폰에서 소리/진동 없이 도착(생존신고용)."""
    if not (TG_TOKEN and TG_CHAT_ID):
        print("[텔레그램 미설정]", msg)
        return
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": TG_CHAT_ID,
        "text": msg,
        "disable_notification": "true" if silent else "false",
    }).encode()
    try:
        urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=20).read()
    except Exception as e:
        print("텔레그램 전송 실패(무시):", e)


def main() -> None:
    # 1) 생존신고 (30분마다 1번, 무음)
    send("🩺 감시 정상 작동중 · 아직 품절", silent=True)

    # 2) 세션 동안 60초 간격 확인
    deadline = time.time() + SESSION_MINUTES * 60
    while time.time() < deadline:
        try:
            html = fetch(PRODUCT_URL)
            if is_in_stock(html):
                send(f"🎸🚨 재입고!! Quad Cortex Mini 지금 구매 가능!\n{PRODUCT_URL}")
                print("IN STOCK ▶ 알림 전송, 세션 종료")
                sys.exit(0)
            print("still sold out")
        except Exception as e:
            print("확인 실패(다음 회차에 재시도):", e)
        time.sleep(CHECK_INTERVAL_SEC)

    print("세션 종료 (30분 뒤 다음 세션 시작)")


if __name__ == "__main__":
    main()
