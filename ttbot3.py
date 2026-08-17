import os
import time
import telebot
import yt_dlp
from telebot import types

TOKEN = "7830957809:AAGs2q6QjUXGpjpobZC_T6zMYnFxmG9JdOo"
bot = telebot.TeleBot(TOKEN)

last_update_time = {}


def make_progress_bar(percent_num):
  filled = int(percent_num // 10)
  empty = 10 - filled
  return "" * filled + "" * empty


def progress_hook(d, message_id, chat_id):
  if d['status'] == 'downloading':
    current_time = time.time()
    if (
        chat_id in last_update_time
        and (current_time - last_update_time[chat_id]) < 1.5
    ):
      return
    last_update_time[chat_id] = current_time

    try:
      p_raw = d.get('_percent_str', '0%').strip().replace('%', '')
      p_float = float(p_raw)
    except:
      p_float = 0.0

    bar = make_progress_bar(p_float)
    speed = d.get('_speed_str', '0 KB/s').strip()
    eta = d.get('_eta_str', 'N/A').strip()

    frames = ['', '', '', '', '']
    current_frame = frames[int(current_time * 2) % len(frames)]

    text = (
        f"{current_frame} **TikTok Video Downloading...**\n\n"
        f" `[{bar}]` **{p_float:.1f}%**\n"
        f" **Speed:** `{speed}`\n"
        f" **ETA:** `{eta}`"
    )

    try:
      bot.edit_message_text(text, chat_id, message_id, parse_mode='Markdown')
    except Exception:
      pass


@bot.message_handler(commands=['start', 'help'])
def start(message):
  bot.reply_to(
      message,
      ' မင်္ဂလာပါ! TikTok link ပို့ပေးပါ၊ Quality ရွေးချယ်နိုင်ပါသည်။',
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
  try:
    data = call.data.split('|', 1)
    quality = data[0]
    url = data[1]

    msg = bot.send_message(
        call.message.chat.id,
        ' *စတင်ပြင်ဆင်နေပါသည်...*',
        parse_mode='Markdown',
    )

    format_opt = 'best' if quality == 'hd' else 'worst'
    filename = f'tiktok_{call.message.chat.id}_{call.message.message_id}.mp4'

    ydl_opts = {
        'format': format_opt,
        'outtmpl': filename,
        'quiet': True,
        'no_warnings': True,
        'progress_hooks': [
            lambda d: progress_hook(d, msg.message_id, call.message.chat.id)
        ],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      ydl.download([url])

    bot.edit_message_text(
        ' **ဒေါင်းလုဒ်ပြီးပါပြီ! Telegram သို့ တင်ပို့နေသည်...**',
        call.message.chat.id,
        msg.message_id,
        parse_mode='Markdown',
    )

    if os.path.exists(filename):
      with open(filename, 'rb') as video:
        bot.send_video(
            call.message.chat.id,
            video,
            caption=' **TikTok Video Downloaded Successfully!**',
            parse_mode='Markdown',
        )
      bot.delete_message(call.message.chat.id, msg.message_id)

  except Exception as e:
    bot.send_message(
        call.message.chat.id,
        f' **အမှားဖြစ်သွားပါသည်:**\n`{str(e)}`',
        parse_mode='Markdown',
    )

  finally:
    if 'filename' in locals() and os.path.exists(filename):
      os.remove(filename)


print('Bot is active...')
bot.polling(none_stop=True)
