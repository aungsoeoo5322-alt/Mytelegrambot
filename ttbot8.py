
cimport os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class DummyServer(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), DummyServer)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()
import re
import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# =========================================================
# BOT TOKEN
# =========================================================
BOT_TOKEN = os.getenv("BOT_TOKEN", "7830957809:AAGs2q6QjUXGpjpobZC_T6zMYnFxmG9JdOo")

TIKTOK_REGEX = re.compile(
    r"(https?://)?(www\.)?(vm\.tiktok\.com|vt\.tiktok\.com|tiktok\.com|www\.tiktok\.com)/[^\s]+",
    re.IGNORECASE,
)

# =========================================================
# Start Command
# =========================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🙏🙏🙏 အားလုံးပဲမင်္ဂလာပါဗျ ကျွန်တော်ကတော့ AungSoeOo ပါ "
        "Tiktok video တွေကို watermark မပါဘဲ quality "
        "ကောင်းကောင်းနဲ့ ဒီ bot မှာ အခမဲ့ Download လုပ်လို့ရပါပြီခင်ဗျာ "
        "အားလုံးကိုကျေးဇူးတင်ပါသည်\n\n"
        "🔗 *TikTok video link တစ်ခု ပို့ပေးပါဗျာ။*"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# =========================================================
# TikTok Link Downloader Engine (API Based)
# =========================================================
async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    message_text = update.message.text.strip()
    match = TIKTOK_REGEX.search(message_text)

    if not match:
        await update.message.reply_text("❌ TikTok link မတွေ့ပါဘူး။ Link မှန်အောင်ပြန်ပို့ပေးပါ။")
        return

    url = match.group(0)
    status_msg = await update.message.reply_text("🔎 TikTok Video (Watermark မပါ) ကို ရယူနေပါတယ်...\n⏳ ခဏစောင့်ပါ...")

    try:
        # TikWM High-Speed Server သို့ ချိတ်ဆက်ခြင်း
        api_url = "https://www.tikwm.com/api/"
        params = {"url": url, "hd": 1}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        
        response = requests.get(api_url, params=params, headers=headers, timeout=15).json()

        if response.get("code") == 0:
            data = response.get("data", {})
            
            # HD သို့မဟုတ် No-Watermark တိုက်ရိုက် Video URL ယူခြင်း
            video_url = data.get("hdplay") or data.get("play")
            title = data.get("title") or "TikTok Video"

            caption = (
                f"🎬 *{title[:120]}*\n\n"
                f"✨ Created by AungSoeOo"
            )

            # Telegram ဆီသို့ Video တိုက်ရိုက် Upload တင်ပေးခြင်း
            await update.message.reply_video(
                video=video_url,
                caption=caption,
                parse_mode="Markdown"
            )
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ Video ရယူလို့မရပါဘူး။ TikTok Link မမှန်တာ သို့မဟုတ် Private Video ဖြစ်နိုင်ပါတယ်။")

    except Exception as e:
        print("ERROR:", e)
        await status_msg.edit_text("❌ Download လုပ်ရာတွင် အမှားအယွင်းရှိသွားပါသည်။ ခဏစောင့်ပြီး ပြန်စမ်းပေးပါ။")

# =========================================================
# Main Function
# =========================================================
def main():
    if not BOT_TOKEN or BOT_TOKEN == "PUT_YOUR_NEW_TOKEN_HERE":
        print("\n❌ BOT_TOKEN မထည့်ရသေးပါဘူး။\n")
        return

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_tiktok))

    print("🚀 Advanced API TikTok Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
