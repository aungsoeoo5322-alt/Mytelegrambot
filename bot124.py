
import os
import requests
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = '8869875129:AAG_MiiTWRsnaKyZV4jMo3neu_gKdfD8v1Q'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

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
        # TikTok TikWm Free API အသုံးပြု၍ HD Video/Photo ဆွဲခြင်း
        api_url = f"https://www.tikwm.com/api/?url={url}"
        response = requests.get(api_url).json()

        if response.get("code") == 0:
            data = response.get("data", {})
            
            # Photo / Slide / Live Photo ဖြစ်ပါက
            if "images" in data and data["images"]:
                for img_url in data["images"]:
                    await update.message.reply_photo(photo=img_url, caption=caption_text)
            
            # Video ဖြစ်ပါက (Watermark မပါ HD)
            else:
                video_url = data.get("play")  # Watermark မပါသော Video Link
                await update.message.reply_video(video=video_url, caption=caption_text, supports_streaming=True)
            
            await msg.delete()
        else:
            await msg.edit_text(" Link မှားယွင်းနေပါသည် သို့မဟုတ် ဒေါင်းလုဒ်ဆွဲ၍ မရပါ။")

    except Exception as e:
        await msg.edit_text(" အမှားအယွင်းတစ်ခု ဖြစ်ပေါ်ခဲ့ပါသည်။")
        logging.error(f"Error: {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_tiktok))
    print("Bot ဖွင့်လှစ်လိုက်ပါပြီ...")
    app.run_polling()
