import os
import requests
import logging
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = '8869875129:AAG_MiiTWRsnaKyZV4jMo3neu_gKdfD8v1Q'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Render မှ PORT ကို တောင်းဆိုသည့်အခါ တုံ့ပြန်ရန် Dummy HTTP Web Server
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running alive!")

def run_health_check_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "ကျွန်တော့်နာမည်ကAungSoeOoပါမြန်မာနိုင်ငံကပါ "
        "ဒီbotကိုကြော်ငြာမပါအခကြေးပေးစရာမလိုပဲအကန့်သတ်မရှိအသုံးပြုနိုင်ရန်ရည်ရွယ်ပါသည်အားလုံးကိုကျေးဇူးတင်ပါသည်"
    )
    await update.message.reply_text(welcome_text)

async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not ("tiktok.com" in url):
        return

    msg = await update.message.reply_text(" ဒေါင်းလုဒ်ဆွဲနေပါသည်၊ ခဏစောင့်ပေးပါ...")
    caption_text = "Creat By AungSoeOo"

    try:
        api_url = f"https://www.tikwm.com/api/?url={url}"
        response = requests.get(api_url).json()

        if response.get("code") == 0:
            data = response.get("data", {})
            if "images" in data and data["images"]:
                for img_url in data["images"]:
                    await update.message.reply_photo(photo=img_url, caption=caption_text)
            else:
                video_url = data.get("play")
                await update.message.reply_video(video=video_url, caption=caption_text, supports_streaming=True)
            await msg.delete()
        else:
            await msg.edit_text(" Link မှားယွင်းနေပါသည် သို့မဟုတ် ဒေါင်းလုဒ်ဆွဲ၍ မရပါ။")

    except Exception as e:
        await msg.edit_text(" အမှားအယွင်းတစ်ခု ဖြစ်ပေါ်ခဲ့ပါသည်။")
        logging.error(f"Error: {e}")

if __name__ == '__main__':
    # Web Server ကို Background Thread ဖြင့် Run ခြင်း
    Thread(target=run_health_check_server, daemon=True).start()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_tiktok))
    print("Bot ဖွင့်လှစ်လိုက်ပါပြီ...")
    app.run_polling()
