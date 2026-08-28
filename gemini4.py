import os
import io
from google import genai
from PIL import Image
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest

GEMINI_KEY = "AQ.Ab8RN6JI2hpLDeIVDtMiewytZxKQYCPRoI6zoJmCfAQWvag7cA"
BOT_TOKEN = "8074860239:AAETPsuLIM-8BWbpCgt4zdHhEmwq85Ok398"

client = genai.Client(api_key="AQ.Ab8RN6JI2hpLDeIVDtMiewytZxKQYCPRoI6zoJmCfAQWvag7cA")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        " Gemini All-in-One AI Bot မှ ကြိုဆိုပါတယ်!\n\n"
        " စာသားများ: မေးခွန်းမေးခြင်း၊ စကားပြောခြင်း\n"
        " ဓာတ်ပုံများ: ဓာတ်ပုံအကြောင်း ရှင်းပြပေးခြင်း\n"
        " အသံဖိုင်များ: Audio ကို စာအဖြစ် ဘာသာပြန်ပေးခြင်း\n"
        " Documents: စာအကျဉ်းချုပ်ပေးခြင်း"
    )
    await update.message.reply_text(welcome_text)

# ၁။ စာသား မေးခွန်းများ
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    status_msg = await update.message.reply_text(" Gemini မှ စဉ်းစားနေပါသည်။...")

    try:
        # gemini-3.6-flash သို့ ပြောင်းလဲထားသည်
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=f"You are a helpful AI assistant. Answer in natural Myanmar language: {user_text}"
        )
        await status_msg.edit_text(response.text)
    except Exception as e:
        await status_msg.edit_text(f" Error: {str(e)}")

# ၂။ ဓာတ်ပုံများ
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text(" ဓာတ်ပုံကို စစ်ဆေးနေပါသည်...")

    try:
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()
        image = Image.open(io.BytesIO(image_bytes))

        prompt = "ဒီဓာတ်ပုံထဲမှာ ဘာတွေပါဝင်လဲဆိုတာနဲ့ အဓိကအချက်တွေကို မြန်မာလို အသေးစိတ် ရှင်းပြပေးပါ။"
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[image, prompt]
        )
        await status_msg.edit_text(response.text)
    except Exception as e:
        await status_msg.edit_text(f" Photo Error: {str(e)}")

# ၃။ အသံဖိုင်များ
async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text(" အသံဖိုင်ကို စစ်ဆေးနေပါသည်...")

    audio_file_path = "temp_audio.mp3"
    try:
        audio_obj = update.message.audio or update.message.voice
        file_info = await context.bot.get_file(audio_obj.file_id)
        await file_info.download_to_drive(audio_file_path)

        uploaded_file = client.files.upload(file=audio_file_path)
        
        prompt = "ဒီအသံဖိုင်ထဲမှာ ပြောထားတဲ့ စကားတွေကို နားထောင်ပြီး အဓိကအချက်တွေကို မြန်မာလို အနှစ်ချုပ် ပြန်ပြောပြပေးပါ။"
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[uploaded_file, prompt]
        )
        await status_msg.edit_text(response.text)

    except Exception as e:
        await status_msg.edit_text(f" Audio Error: {str(e)}")
    finally:
        if os.path.exists(audio_file_path):
            os.remove(audio_file_path)

# ၄။ Document ဖိုင်များ
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text(" ဖိုင်အချက်အလက်များကို ဖတ်ရှုနေပါသည်...")

    doc_obj = update.message.document
    doc_path = f"temp_{doc_obj.file_name}"
    
    try:
        file_info = await context.bot.get_file(doc_obj.file_id)
        await file_info.download_to_drive(doc_path)

        uploaded_file = client.files.upload(file=doc_path)
        
        prompt = "ဒီ Document ဖိုင်ထဲက အဓိက အချက်အလက်တွေကို မြန်မာလို အနှစ်ချုပ် ရှင်းပြပေးပါ။"
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[uploaded_file, prompt]
        )
        await status_msg.edit_text(response.text)

    except Exception as e:
        await status_msg.edit_text(f" Document Error: {str(e)}")
    finally:
        if os.path.exists(doc_path):
            os.remove(doc_path)

if __name__ == '__main__':
    request_kwargs = HTTPXRequest(connect_timeout=60, read_timeout=60)
    app = ApplicationBuilder().token(BOT_TOKEN).request(request_kwargs).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.AUDIO | filters.VOICE, handle_audio))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    print("All-in-One Gemini Bot စတင်ပါပြီ...")
    app.run_polling()
