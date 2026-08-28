import os
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

TOKEN = '8281539844:AAFjBcw0JWXGH1vKeuwHIRX712joacrfzxA'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# မိတ်ဆက် စာသား
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "ကျွန်တော့်နာမည်ကAungSoeOoပါမြန်မာနိုင်ငံကပါ "
        "ဒီbotကိုကြော်ငြာမပါအခကြေးပေးစရာမလိုပဲအကန့်သတ်မရှိအသုံးပြုနိုင်ရန်ရည်ရွယ်ပါသည်အားလုံးကိုကျေးဇူးတင်ပါသည်\n\n"
        "🔊 မြန်မာစာ သို့မဟုတ် အင်္ဂလိပ်စာ ရိုက်ပို့လိုက်ပါက အသံဖိုင်အဖြစ် ပြောင်းလဲပေးမည်ဖြစ်ပါသည်။"
    )
    await update.message.reply_text(welcome_text)

# စာသားရောက်လာပါက ကျား/မ အသံ ရွေးခိုင်းသည့် ခလုတ်ပြခြင်း
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    if not user_text:
        return

    # User ရိုက်ပို့လိုက်သော စာသားကို ခန့်မှန်းသိမ်းဆည်းထားခြင်း
    context.user_data['text_to_convert'] = user_text

    keyboard = [
        [
            InlineKeyboardButton("👩 အမျိုးသမီးအသံ (Nilar)", callback_data='voice_female'),
            InlineKeyboardButton("👨 အမျိုးသားအသံ (Thiha)", callback_data='voice_male')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("🗣️ ကျေးဇူးပြု၍ အသံအမျိုးအစား ရွေးချယ်ပေးပါ:", reply_markup=reply_markup)

# ခလုတ်နှိပ်လိုက်သည့်အခါ အသံဖိုင် ပြောင်းပေးသည့် Function
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_text = context.user_data.get('text_to_convert')
    if not user_text:
        await query.edit_message_text("❌ စာသား အသစ်ပြန်ပို့ပေးပါ။")
        return

    # ရွေးချယ်လိုက်သော အသံအမျိုးအစား စစ်ဆေးခြင်း
    if query.data == 'voice_male':
        selected_voice = "my-MM-ThihaNeural"
        voice_label = "👨 အမျိုးသားအသံ"
    else:
        selected_voice = "my-MM-NilarNeural"
        voice_label = "👩 အမျိုးသမီးအသံ"

    await query.edit_message_text(f"🔊 {voice_label}ဖြင့် အသံဖိုင် ဖန်တီးနေပါသည်...")

    file_path = f"voice_{query.from_user.id}.mp3"

    try:
        # Edge TTS ဖြင့် အသံဖိုင် ဖန်တီးခြင်း (rate='+0%' သဘာဝအတိုင်း အသံထွက်စေခြင်း)
        communicate = edge_tts.Communicate(user_text, selected_voice, rate="+0%")
        await communicate.save(file_path)

        with open(file_path, 'rb') as audio:
            await query.message.reply_audio(
                audio=audio,
                caption="Creat By AungSoeOo",
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
    request_kwargs = HTTPXRequest(connect_timeout=60, read_timeout=60)
    app = ApplicationBuilder().token(TOKEN).request(request_kwargs).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(button_click))

    print("TTS Bot ဖွင့်လှစ်လိုက်ပါပြီ...")
    app.run_polling()
