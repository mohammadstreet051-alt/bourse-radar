import time
import requests
from datetime import datetime, timezone, timedelta

# ========================================================
# تنظیمات ربات 
# ========================================================
BALE_TOKEN = "471791104:Lp61JTQABDJuiJaGgYdEFSW7qckAtpu9EEk"
CHAT_ID = "YOUR_PERSONAL_CHAT_ID" # اگر خالی بماند، ربات خودکار آخرین چت را پیدا می‌کند

def send_to_user(text):
    chat_id = CHAT_ID
    if chat_id == "YOUR_PERSONAL_CHAT_ID":
        updates_url = f"https://tapi.bale.ai/bot{BALE_TOKEN}/getUpdates"
        try:
            res = requests.get(updates_url, timeout=10).json()
            if res.get("ok") and res.get("result"):
                chat_id = res["result"][-1]["message"]["chat"]["id"]
            else:
                print("خطا: لطفاً اول به ربات در بله یک پیام بفرستید تا چت باز شود.")
                return
        except Exception as e:
            print("Error getting chat_id:", e)
            return

    url = f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print("Bale Error:", e)

def get_iran_datetime():
    utc_now = datetime.now(timezone.utc)
    iran_time = utc_now.astimezone(timezone(timedelta(hours=3, minutes=30)))
    date_str = iran_time.strftime("%Y/%m/%d")
    time_str = iran_time.strftime("%H:%M:%S")
    return date_str, time_str

if __name__ == "__main__":
    cur_date, cur_time = get_iran_datetime()
    
    # نمونه پیام تستی سیگنال
    sample_signal_msg = (
        f"🟡 **[پیام تستی] سیگنال صندوق و سهام طلا (بورس)** 🟡\n"
        f"━━━━━━━━━━━━━━\n"
        f"📌 نماد: #عیار (صندوق طلای عیار)\n"
        f"💵 آخرین قیمت: ۶۴,۲۵۰ ریال (+۴.۸٪)\n\n"
        f"🎯 علت سیگنال (تست سیستم):\n"
        f"✅ ورود سنگین پول هوشمند به صندوق طلا\n"
        f"✅ قدرت خرید بالا و صف خرید پایدار\n\n"
        f"📊 وضعیت تابلو:\n"
        f"• قدرت خریدار: ۲.۶ برابر\n"
        f"• سرانه خرید: ۷۵ میلیون تومان\n"
        f"• خالص ورود پول: ۱۸ میلیارد تومان\n\n"
        f"📅 تاریخ: {cur_date}\n"
        f"⏰ ساعت: {cur_time}\n"
        f"🤖 @BourseGoldRadar_bot"
    )
    
    print("در حال ارسال پیام تستی به بله...")
    send_to_user(sample_signal_msg)
    print("ارسال شد!")
