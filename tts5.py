import os
from flask import Flask
from threading import Thread
import edge_tts
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler, 
    filters, 
    ContextTypes
)
from telegram.request import HTTPXRequest

# Flask Server for Render
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Bot is running online!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

TOKEN = os.getenv('BOT_TOKEN', '8281539844:AAFjBcw0JWXGH1vKeuwHIRX712joacrfzxA')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "ကျွန်တော့်နာမည်က AungSoeOo ပါ မြန်မာနိုင်ငံကပါ။\n"
        "ဒီ Bot ကို အခကြေးပေးစရာမလိုဘဲ အကန့်အသတ်မရှိ အသုံးပြုနိုင်ပါသည်။\n\n"
        "🔊 စာသား (Text) သို့မဟုတ် .txt ဖိုင် ပို့ပေးပါက အသံဖိုင်အဖြစ် ပြောင်းလဲပေးပါမည်။"
    )
    await update.message.reply_text(welcome_text)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    if not user_text:
        return
    context.user_data['text_to_convert'] = user_text
    await show_voice_options(update)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    if not document.file_name.endswith('.txt'):
        await update.message.reply_text("❌ ကျေးဇူးပြု၍ .txt ဖိုင်အမျိုးအစားကိုပဲ ပို့ပေးပါ။")
        return

    file = await context.bot.get_file(document.file_id)
    file_bytes = await file.download_as_bytearray()
    
    try:
        user_text = file_bytes.decode('utf-8').strip()
    except UnicodeDecodeError:
        user_text = file_bytes.decode('utf-16', errors='ignore').strip()

    if not user_text:
        await update.message.reply_text("❌ ဖိုင်ထဲတွင် မည်သည့် စာသားမျှ မရှိပါ။")
        return

    context.user_data['text_to_convert'] = user_text
    await show_voice_options(update)

# အသံရွေးချယ်ရန်နှင့် အစမ်းနားထောင်ရန် Menu
async def show_voice_options(update: Update):
    keyboard = [
        [
            InlineKeyboardButton("👩 Nilar (ပုံမှန်အသံ)", callback_data='voice_female_norm'),
            InlineKeyboardButton("👩 Nilar (အေးဆေး/နားထောင်ကောင်း)", callback_data='voice_female_slow')
        ],
        [
            InlineKeyboardButton("👨 Thiha (ပုံမှန်အသံ)", callback_data='voice_male_norm'),
            InlineKeyboardButton("👨 Thiha (အေးဆေး/နားထောင်ကောင်း)", callback_data='voice_male_slow')
        ],
        [
            InlineKeyboardButton("🎧 Nilar အသံအစမ်းနားထောင်မည်", callback_data='sample_female'),
            InlineKeyboardButton("🎧 Thiha အသံအစမ်းနားထောင်မည်", callback_data='sample_male')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🗣️ ကျေးဇူးပြု၍ အသံအမျိုးအစားနှင့် အရှိန် စိတ်ကြိုက်ရွေးချယ်ပါ:", reply_markup=reply_markup)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    # အသံ အစမ်းနားထောင်ခြင်း (Sample Audio)
    if data.startswith('sample_'):
        voice = "my-MM-NilarNeural" if data == 'sample_female' else "my-MM-ThihaNeural"
        sample_text = "မင်္ဂလာပါရှင်၊ ဒါကတော့ အသံအစမ်းနားထောင်ခြင်း ဖြစ်ပါတယ်ရှင့်။" if data == 'sample_female' else "မင်္ဂလာပါခင်ဗျာ၊ ဒါကတော့ အသံအစမ်းနားထောင်ခြင်း ဖြစ်ပါတယ်ခင်ဗျာ။"
        
        file_path = f"sample_{query.from_user.id}.mp3"
        try:
            communicate = edge_tts.Communicate(sample_text, voice, rate="+0%")
            await communicate.save(file_path)
            with open(file_path, 'rb') as audio:
                await query.message.reply_audio(audio=audio, caption="🎧 အသံနမူနာ စမ်းသပ်ချက်")
        except Exception as e:
            logging.error(f"Sample error: {e}")
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
        return

    # တကယ့် စာသားကို အသံပြောင်းခြင်း
    user_text = context.user_data.get('text_to_convert')
    if not user_text:
        await query.edit_message_text("❌ စာသား သို့မဟုတ် ဖိုင် အသစ်ပြန်ပို့ပေးပါ။")
        return

    # အသံနှင့် Rate (အရှိန်) သတ်မှတ်ချက်
    voice_config = {
        'voice_female_norm': ("my-MM-NilarNeural", "+0%", "👩 အမျိုးသမီး (ပုံမှန်)"),
        'voice_female_slow': ("my-MM-NilarNeural", "-10%", "👩 အမျိုးသမီး (အေးဆေး)"),
        'voice_male_norm': ("my-MM-ThihaNeural", "+0%", "👨 အမျိုးသား (ပုံမှန်)"),
        'voice_male_slow': ("my-MM-ThihaNeural", "-10%", "👨 အမျိုးသား (အေးဆေး)"),
    }

    selected_voice, rate, voice_label = voice_config.get(data, ("my-MM-NilarNeural", "+0%", "👩 အမျိုးသမီး"))

    await query.edit_message_text(f"🔊 {voice_label} ဖြင့် အသံဖိုင် ဖန်တီးနေပါသည်...")

    file_path = f"voice_{query.from_user.id}.mp3"

    try:
        communicate = edge_tts.Communicate(user_text, selected_voice, rate=rate)
        await communicate.save(file_path)

        with open(file_path, 'rb') as audio:
            await query.message.reply_audio(
                audio=audio,
                caption="Created By AungSoeOo",
                title=f"TTS ({voice_label})"
            )
        await query.delete_message()

    except Exception as e:
        await query.message.reply_text("❌ အသံပြောင်းရာတွင် အမှားအယွင်း ဖြစ်ပေါ်ခဲ့ပါသည်။")
        logging.error(f"Error: {e}")

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == '__main__':
    keep_alive()

    request_kwargs = HTTPXRequest(connect_timeout=60, read_timeout=60)
    app = ApplicationBuilder().token(TOKEN).request(request_kwargs).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(CallbackQueryHandler(button_click))

    print("TTS Bot ဖွင့်လှစ်လိုက်ပါပြီ...")
    app.run_polling()
