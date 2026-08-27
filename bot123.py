import os
import glob
import logging
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Telegram Bot Token
TOKEN = '8869875129:AAG_MiiTWRsnaKyZV4jMo3neu_gKdfD8v1Q'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 1. /start command မိတ်ဆက် စာသား
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "ကျွန်တော့်နာမည်ကAungSoeOoပါမြန်မာနိုင်ငံကပါ "
        "ဒီbotကိုကြော်ငြာမပါအခကြေးပေးစရာမလိုပဲအကန့်သတ်မရှိအသုံးပြုနိုင်ရန်ရည်ရွယ်ပါသည်အားလုံးကိုကျေးဇူးတင်ပါသည်"
    )
    await update.message.reply_text(welcome_text)

# 2. TikTok Link များကို Download လုပ်ပေးသည့် Function
async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    # TikTok Link ဟုတ်မဟုတ် စစ်ဆေးခြင်း
    if not ("tiktok.com" in url or "vt.tiktok.com" in url):
        return

    msg = await update.message.reply_text(" ဒေါင်းလုဒ်ဆွဲနေပါသည်၊ ခဏစောင့်ပေးပါ...")
    caption_text = "Creat By AungSoeOo"
    
    # File နာမည် သတ်မှတ်ခြင်း
    output_template = f"downloads/{update.message.from_user.id}_%(id)s.%(ext)s"

    # yt-dlp Options (Watermark မပါ HD Video & Photos ရရှိရန်)
    ydl_opts = {
        'outtmpl': output_template,
        'format': 'bestvideo+bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
    }

    try:
        os.makedirs("downloads", exist_ok=True)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # ဒေါင်းလုဒ်ဆွဲထားသော ဖိုင်များကို ရှာဖွေခြင်း
        files = glob.glob(f"downloads/{update.message.from_user.id}_*")

        if not files:
            await msg.edit_text(" ဒေါင်းလုဒ်ဆွဲ၍ မရပါ သို့မဟုတ် Save ပိတ်ထားသော Content အမျိုးအစားဖြစ်နေပါသည်။")
            return

        for file_path in files:
            # Video ဖိုင်ဖြစ်ပါက
            if file_path.endswith(('.mp4', '.mkv', '.webm')):
                with open(file_path, 'rb') as video:
                    await update.message.reply_video(
                        video=video,
                        caption=caption_text,
                        supports_streaming=True
                    )
            # Photo / Slide / Live Photo ဖြစ်ပါက
            elif file_path.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                with open(file_path, 'rb') as photo:
                    await update.message.reply_photo(
                        photo=photo,
                        caption=caption_text
                    )
            
            # ပို့ပြီးပါက ဖိုင်အား ရှင်းထုတ်ခြင်း
            if os.path.exists(file_path):
                os.remove(file_path)

        await msg.delete()

    except Exception as e:
        await msg.edit_text(f" အမှားအယွင်းတစ်ခု ဖြစ်ပေါ်ခဲ့ပါသည်။")
        logging.error(f"Error: {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_tiktok))

    print("Bot ဖွင့်လှစ်လိုက်ပါပြီ...")
    app.run_polling()

