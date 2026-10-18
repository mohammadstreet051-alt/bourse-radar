import time
import requests
from datetime import datetime, timezone, timedelta

# ========================================================
# اطلاعات ربات و کانال طلا (مربوط به گلد رادار)
# ========================================================
BALE_TOKEN = "471791104:Lp61JTQABDJuiJaGgYdEFSW7qckAtpu9EEk"
CHANNEL_ID = "@GoldRadar_AI"

# آدرس دریافت قیمت انس جهانی و طلا
API_URL = "https://api.coincap.io/v2/rates/gold" # یا وب‌سرویس‌های رایگان طلا
# فعلا برای تست ساختار، ساختار پایه را می‌گذاریم

def send_to_bale(text):
    url = f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": text}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print("Bale Error:", e)

def get_iran_time():
    utc_now = datetime.now(timezone.utc)
    return utc_now.astimezone(timezone(timedelta(hours=3, minutes=30)))

if __name__ == "__main__":
    now_ir = get_iran_time()
    send_to_bale(
        "🟡 **رادار انس و طلای جهانی (`@GoldRadarAI_bot`) با موفقیت راه‌اندازی شد!**\n"
        f"⏰ زمان تست سیستم: {now_ir.strftime('%H:%M:%S')}\n"
        "این کانال کاملاً مجزا از بورس ایران، به صورت خودکار تحولات بازار طلا را رصد خواهد کرد."
    )
