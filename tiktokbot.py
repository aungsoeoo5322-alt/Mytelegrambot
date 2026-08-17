import os
import telebot
import yt_dlp

# သင်၏ Bot Token
BOT_TOKEN = "7830957809:AAGs2q6QjUXGpjpobZC_T6zMYnFxmG9JdOo"
bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
  bot.reply_to(
      message,
      "👋 မင်္ဂလာပါ! TikTok Video Link ပို့ပေးပါ။ ဗီဒီယို"
      " ဒေါင်းလုဒ်ဆွဲပေးပါမည်။",
  )


@bot.message_handler(func=lambda message: True)
def process_tiktok_link(message):
  url = message.text.strip()

  # TikTok Link ဟုတ်မဟုတ် စစ်ဆေးခြင်း
  if "tiktok.com" not in url:
    bot.reply_to(
        message, "❌ ကျေးဇူးပြု၍ မှန်ကန်သော TikTok link ကိုသာ ပို့ပေးပါ။"
    )
    return

  status_msg = bot.reply_to(
      message, "⏳ TikTok ဗီဒီယို ဒေါင်းလုဒ်ဆွဲနေပါသည်။ ခဏစောင့်ပါ..."
  )
  output_filename = f"tiktok_{message.chat.id}_{message.message_id}.mp4"

  ydl_opts = {
      "outtmpl": output_filename,
      "format": "bestvideo+bestaudio/best",
      "quiet": True,
      "no_warnings": True,
  }

  try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      ydl.download([url])

    # Telegram သို့ ဗီဒီယို ပြန်ပို့ပေးခြင်း
    if os.path.exists(output_filename):
      with open(output_filename, "rb") as video:
        bot.send_video(
            message.chat.id,
            video,
            caption="✅ ဒေါင်းလုဒ်ဆွဲပြီးပါပြီ!",
            reply_to_message_id=message.message_id,
        )
      bot.delete_message(message.chat.id, status_msg.message_id)
    else:
      bot.edit_message_text(
          "❌ ဗီဒီယို ဖိုင်ရှာမတွေ့ပါ။",
          chat_id=message.chat.id,
          message_id=status_msg.message_id,
      )

  except Exception as e:
    bot.edit_message_text(
        f"❌ ဒေါင်းလုဒ်ဆွဲရာတွင် အမှားအယွင်းရှိပါသည်:\n`{str(e)}`",
        chat_id=message.chat.id,
        message_id=status_msg.message_id,
        parse_mode="Markdown",
    )

  finally:
    # ဒေါင်းလုဒ်ဆွဲထားသော ဖိုင်ကို ပြန်ဖျက်၍ Storage ရှင်းခြင်း
    if os.path.exists(output_filename):
      os.remove(output_filename)


print("Bot active and listening...")
bot.polling(none_stop=True)

