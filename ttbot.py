import os
import telebot
import yt_dlp
from telebot import types

# သင့်၏ Bot Token
TOKEN = "7830957809:AAGs2q6QjUXGpjpobZC_T6zMYnFxmG9JdOo"
bot = telebot.TeleBot(TOKEN)


# Progress Bar အချိန်နဲ့တစ်ပြေးညီ ပြသပေးမည့် Function
def progress_hook(d, message_id, chat_id):
  if d['status'] == 'downloading':
    p = d.get('_percent_str', '0%')
    speed = d.get('_speed_str', 'N/A')
    text = f" ဒေါင်းလုဒ်ဆွဲနေသည်: {p}\n အမြန်နှုန်း: {speed}"
    try:
      bot.edit_message_text(text, chat_id, message_id)
    except:
      pass


@bot.message_handler(commands=['start', 'help'])
def start(message):
  bot.reply_to(
      message,
      ' မင်္ဂလာပါ! TikTok link ပို့ပေးပါ၊ Quality ရွေးပြီး'
      ' ဒေါင်းလုဒ်ဆွဲနိုင်ပါပြီ။',
  )


@bot.message_handler(func=lambda message: 'tiktok.com' in message.text)
def handle_link(message):
  url = message.text.strip()
  markup = types.InlineKeyboardMarkup()
  markup.add(
      types.InlineKeyboardButton(
          ' HD Quality (Best)', callback_data=f'hd|{url}'
      )
  )
  markup.add(
      types.InlineKeyboardButton(
          ' SD Quality (Fast)', callback_data=f'sd|{url}'
      )
  )
  bot.reply_to(message, ' ဗီဒီယို Quality ရွေးချယ်ပါ:', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
  data = call.data.split('|')
  quality = data[0]
  url = data[1]

  msg = bot.send_message(
      call.message.chat.id, ' ဒေါင်းလုဒ်စတင်ရန် ပြင်ဆင်နေသည်...'
  )

  format_opt = (
      'bestvideo+bestaudio/best' if quality == 'hd' else 'worstvideo+worstaudio/worst'
  )
  filename = f'tiktok_{call.message.chat.id}_{call.message.message_id}.mp4'

  ydl_opts = {
      'format': format_opt,
      'outtmpl': filename,
      'quiet': True,
      'progress_hooks': [
          lambda d: progress_hook(d, msg.message_id, call.message.chat.id)
      ],
  }

  try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      ydl.download([url])

    bot.edit_message_text(
        ' ဒေါင်းလုဒ်ပြီးပါပြီ! Telegram သို့ တင်ပို့နေသည်...',
        call.message.chat.id,
        msg.message_id,
    )

    if os.path.exists(filename):
      with open(filename, 'rb') as video:
        bot.send_video(
            call.message.chat.id,
            video,
            caption=' ဒေါင်းလုဒ်ဆွဲပြီးပါပြီ!',
            reply_to_message_id=call.message.reply_to_message.message_id,
        )
      bot.delete_message(call.message.chat.id, msg.message_id)

  except Exception as e:
    bot.edit_message_text(
        f' အမှားဖြစ်သွားပါသည်: {str(e)}',
        call.message.chat.id,
        msg.message_id,
    )

  finally:
    if os.path.exists(filename):
      os.remove(filename)


print('Bot is running...')
bot.polling(none_stop=True)

