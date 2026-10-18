import time
import requests
from datetime import datetime, timezone, timedelta

# ========================================================
# تنظیمات اختصاصی ربات (ارسال مستقیم به چت شخصی شما در بله)
# ========================================================
BALE_TOKEN = "471791104:Lp61JTQABDJuiJaGgYdEFSW7qckAtpu9EEk"
CHAT_ID = "YOUR_PERSONAL_CHAT_ID"  # اگر خالی بماند، ربات خودکار آخرین چت را پیدا می‌کند

API_URL = "https://Api.BrsApi.ir/Tsetmc/AllSymbols.php?key=Free"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 OPR/106.0.0.0",
    "Accept": "application/json, text/plain, */*"
}

prev_state = {}
sent_alerts = set()

def send_to_user(text):
    """ارسال پیام مستقیم به چت شخصی شما در بله"""
    chat_id = CHAT_ID
    if chat_id == "YOUR_PERSONAL_CHAT_ID":
        updates_url = f"https://tapi.bale.ai/bot{BALE_TOKEN}/getUpdates"
        try:
            res = requests.get(updates_url, timeout=10).json()
            if res.get("ok") and res.get("result"):
                chat_id = res["result"][-1]["message"]["chat"]["id"]
            else:
                print("خطا: لطفاً اول به ربات در بله یک پیام (مثل /start) بفرستید تا چت باز شود.")
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
    """محاسبه تاریخ و ساعت دقیق به وقت ایران"""
    utc_now = datetime.now(timezone.utc)
    iran_time = utc_now.astimezone(timezone(timedelta(hours=3, minutes=30)))
    date_str = iran_time.strftime("%Y/%m/%d")
    time_str = iran_time.strftime("%H:%M:%S")
    return date_str, time_str

def run_market_scanner():
    date_str, time_str = get_iran_datetime()
    
    # تست اتصال و ارسال پیام نمونه در اولین اجرا
    current_hour_min = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=3, minutes=30))).strftime("%H:%M")
    
    # ارسال پیام نمونه تستی برای اطمینان از عملکرد سیستم
    test_msg = (
        f"🎯 **[تست سیستم] اسکنر جامع کل بازار بورس** 🎯\n"
        f"━━━━━━━━━━━━━━\n"
        f"📌 نماد: #مثال_سهم\n"
        f"💵 آخرین قیمت: ۲۵,۴۰۰ ریال (+۴.۸٪)\n\n"
        f"🔍 دلایل شکار سیستم:\n"
        f"✅ ورود سنگین پول هوشمند و کدهای درشت\n\n"
        f"📊 وضعیت تابلو و جریان پول:\n"
        f"• قدرت خریدار حقیقی: ۲.۴ برابر\n"
        f"• سرانه خرید کدهای درشت: ۶۵ میلیون تومان\n"
        f"• خالص ورود پول: ۱۵.۸ میلیارد تومان\n\n"
        f"📈 **مدیریت ریسک (پیشنهادی):**\n"
        f"🛑 حد ضرر: `۲۴,۳۸۴` ریال\n"
        f"🎯 هدف اول: `۲۶,۶۷۰` ریال\n"
        f"🎯 هدف دوم: `۲۷,۹۴۰` ریال\n\n"
        f"📅 تاریخ: {date_str}\n"
        f"⏰ ساعت: {time_str}\n"
        f"🤖 دستیار هوشمند بورس"
    )
    send_to_user(test_msg)

    # اگر خارج از تایم بازار است، همینجا متوقف شو (اما پیام تست را فرستاده است)
    if not ("08:55" <= current_hour_min <= "12:35"):
        return

    # حلقه اسکن بازار در ساعات معاملاتی
    for cycle in range(50):
        c_time = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=3, minutes=30))).strftime("%H:%M")
        if not ("08:55" <= c_time <= "12:35"):
            break

        try:
            response = requests.get(API_URL, headers=HEADERS, timeout=15)
            if response.status_code == 200:
                data = response.json()
            else:
                time.sleep(30)
                continue
        except Exception:
            time.sleep(30)
            continue

        symbols_list = data if isinstance(data, list) else data.get('data', [])

        for item in symbols_list:
            try:
                sym = item.get('l18', '')
                
                # فیلتر نمادهای نامعتبر، اوراق، حق تقدم‌ها و صندوق‌های درآمد ثابت
                if not sym or any(x in sym for x in ['ح', 'ض', 'ط', 'ص', 'اخزا', 'اعتماد', 'صندوق درآمد ثابت']) or sym[-1].isdigit():
                    continue

                last = float(item.get('pl', 0))       
                yest = float(item.get('py', 0))       
                tvol = float(item.get('tvol', 0))     
                tval = float(item.get('tval', 0))     
                tmax = float(item.get('tmax', 0))     
                tmin = float(item.get('tmin', 0))     
                high_p = float(item.get('pmax', last))
                low_p = float(item.get('pmin', last))

                buy_vol_i = float(item.get('Buy_I_Volume', 0))
                buy_cnt_i = float(item.get('Buy_CountI', 1))
                sell_vol_i = float(item.get('Sell_I_Volume', 0))
                sell_cnt_i = float(item.get('Sell_CountI', 1))

                qd1 = float(item.get('qd1', 0))
                pd1 = float(item.get('pd1', 0))
                qo1 = float(item.get('qo1', 0))
                po1 = float(item.get('po1', 0))

                # فیلتر نقدشوندگی (ارزش معاملات روزانه حداقل ۵ میلیارد تومان)
                if tval < 50_000_000_000 or buy_cnt_i < 5 or sell_cnt_i < 5:
                    continue

                buy_per_cap = buy_vol_i / buy_cnt_i
                sell_per_cap = sell_vol_i / sell_cnt_i
                power = round(buy_per_cap / (sell_per_cap + 1e-5), 2)
                buy_cap_m = round((buy_per_cap * last) / 10_000_000, 1) 
                net_money_b = round(((buy_vol_i - sell_vol_i) * last) / 10_000_000_000, 2) 
                pct = round(((last - yest) / yest) * 100, 2)

                close_pos = (last - low_p) / ((high_p - low_p) + 1e-5)
                old = prev_state.get(sym, {'qd1': qd1, 'qo1': qo1, 'last': last})

                buy_reasons = []
                
                if power >= 2.0 and buy_cap_m >= 45 and net_money_b >= 2.5 and close_pos >= 0.7:
                    buy_reasons.append("💰 ورود سنگین پول هوشمند و کدهای درشت")

                if (tmax - last) / yest <= 0.005 and pd1 == tmax:
                    if old['last'] < tmax and last == tmax and tval > 150_000_000_000:
                        buy_reasons.append("🔒 قفل شدن صف خرید با ارزش معاملات بالا")

                if po1 == tmin and old['qo1'] > 500_000 and qo1 < old['qo1'] * 0.45:
                    buy_reasons.append("💥 بلعیده شدن صف فروش و پتانسیل رشد شارپ")

                prev_state[sym] = {'qd1': qd1, 'qo1': qo1, 'last': last}

                if buy_reasons and f"BUY_{sym}" not in sent_alerts:
                    cur_date, cur_time = get_iran_datetime()
                    
                    stop_loss = int(last * 0.96)   
                    target_1 = int(last * 1.05)    
                    target_2 = int(last * 1.10)    

                    msg = (
                        f"🎯 **سیگنال خرید کل بازار بورس** 🎯\n"
                        f"━━━━━━━━━━━━━━\n"
                        f"📌 نماد: #{sym}\n"
                        f"💵 آخرین قیمت: {int(last):,} ریال ({pct:+}%)\n\n"
                        f"🔍 دلایل شکار سیستم:\n" + "\n".join([f"✅ {r}" for r in buy_reasons]) + "\n\n"
                        f"📊 وضعیت تابلو و جریان پول:\n"
                        f"• قدرت خریدار حقیقی: {power} برابر\n"
                        f"• سرانه خرید کدهای درشت: {buy_cap_m} میلیون تومان\n"
                        f"• خالص ورود پول: {net_money_b:+} میلیارد تومان\n\n"
                        f"📈 **مدیریت ریسک (پیشنهادی):**\n"
                        f"🛑 حد ضرر (Stop Loss): `{stop_loss:,}` ریال\n"
                        f"🎯 هدف اول (Target 1): `{target_1:,}` ریال\n"
                        f"🎯 هدف دوم (Target 2): `{target_2:,}` ریال\n\n"
                        f"📅 تاریخ: {cur_date}\n"
                        f"⏰ ساعت: {cur_time}\n"
                        f"🤖 دستیار هوشمند بورس"
                    )
                    send_to_user(msg)
                    sent_alerts.add(f"BUY_{sym}")

            except Exception:
                continue

        time.sleep(30)

if __name__ == "__main__":
    run_market_scanner()
