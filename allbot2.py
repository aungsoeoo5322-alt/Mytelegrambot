import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp

# --- Render အတွက် Dummy Server (Port Error ဖြေရှင်းရန်) ---
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), DummyServer)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# --- Telegram Bot Config ---
BOT_TOKEN = "8997210680:AAHik7Mr2WER4_y8LLFijr4SWP03dRlBkIQ"
user_links = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 မင်္ဂလာပါ! TikTok, YouTube, Facebook, Pinterest ဗီဒီယို Link များကို ပို့ပေးပါ။\n"
        "လိုချင်သော Quality ကို ရွေးချယ်ပြီး ဒေါင်းလုဒ်ဆွဲပေးပါမည်။"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        await update.message.reply_text("⚠️ ကျေးဇူးပြု၍ မှန်ကန်သော Video Link ကို ပို့ပေးပါရှင်။")
        return

    user_id = update.effective_user.id
    user_links[user_id] = url

    keyboard = [
        [
            InlineKeyboardButton("360p (Low)", callback_data="360"),
            InlineKeyboardButton("720p (HD)", callback_data="720"),
        ],
        [
            InlineKeyboardButton("1080p (FHD)", callback_data="1080"),
            InlineKeyboardButton("Audio (MP3)", callback_data="mp3"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🎬 လိုချင်သော Quality ကို ရွေးချယ်ပါ -", reply_markup=reply_markup)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    url = user_links.get(user_id)
    quality = query.data

    if not url:
        await query.edit_message_text("❌ Error: Link သက်တမ်းကုန်သွားပါပြီ။ Link ကို ပြန်လည်ပို့ပေးပါ။")
        return

    await query.edit_message_text(f"⏳ {quality} အရည်အသွေးဖြင့် ဒေါင်းလုဒ်ဆွဲနေပါသည်။ ခဏစောင့်ပေးပါ...")

    output_filename = f"file_{user_id}"

    # YouTube Bot Block ကျော်လွှားရန် Client Settings
    common_opts = {
        'quiet': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'android', 'mweb']
            }
        }
    }

    if quality == "mp3":
        ydl_opts = {
            **common_opts,
            'format': 'bestaudio/best',
            'outtmpl': f'{output_filename}.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        final_file = f"{output_filename}.mp3"
    else:
        ydl_opts = {
            **common_opts,
            'format': f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best',
            'outtmpl': f'{output_filename}.mp4',
        }
        final_file = f"{output_filename}.mp4"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await query.message.reply_text("📤 Telegram သို့ တင်ပို့နေပါပြီ...")
        
        if os.path.exists(final_file):
            with open(final_file, 'rb') as file:
                if quality == "mp3":
                    await context.bot.send_audio(
                        chat_id=user_id, 
                        audio=file, 
                        write_timeout=300, 
                        connect_timeout=300, 
                        read_timeout=300
                    )
                else:
                    await context.bot.send_video(
                        chat_id=user_id, 
                        video=file, 
                        write_timeout=300, 
                        connect_timeout=300, 
                        read_timeout=300
                    )
            
            os.remove(final_file)
        else:
            await query.message.reply_text("❌ ဒေါင်းလုဒ်ဆွဲထားသော ဖိုင်ကို ရှာမတွေ့ပါ။")

    except Exception as e:
        await query.message.reply_text(f"❌ အမှားအယွင်းရှိပါသည်: {str(e)}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()

