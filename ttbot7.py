import asyncio
import os
from pathlib import Path
import re
import tempfile
import urllib.request

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import yt_dlp

# =========================================================
# BOT TOKEN
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "7830957809:AAGs2q6QjUXGpjpobZC_T6zMYnFxmG9JdOo")

DOWNLOAD_DIR = Path(tempfile.gettempdir()) / "tiktok_bot"
DOWNLOAD_DIR.mkdir(exist_ok=True)

user_jobs = {}

TIKTOK_REGEX = re.compile(
    r"(https?://)?(www\.)?(vm\.tiktok\.com|vt\.tiktok\.com|"
    r"tiktok\.com|www\.tiktok\.com)/[^\s]+",
    re.IGNORECASE,
)

# TikTok Anti-Bot ကျော်လွှားရန် အဆင့်မြင့် Settings
COMMON_YTDLP_OPTIONS = {
    "quiet": True,
    "no_warnings": True,
    "nocheckcertificate": True,
    "user_agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "extractor_args": {
        "tiktok": {
            "app_version": "33.8.3",
            "manifest_app_version": "33.8.3",
        }
    },
}

def unshorten_url(url):
    """vt.tiktok.com short links များကို တိုက်ရိုက် Full URL သို့ ပြောင်းလဲခြင်း"""
    try:
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": COMMON_YTDLP_OPTIONS["user_agent"]}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.geturl()
    except Exception:
        return url

# =========================================================
# Start
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🙏🙏🙏 အားလုံးပဲမင်္ဂလာပါဗျ ကျွန်တော်ကတော့ AungSoeOo ပါ "
        "Tiktok video တွေကို watermark မပါဘဲ qualitly "
        "ကောင်းကောင်းနဲ့ ဒီ bot မှာ အခမဲ့ Download လုပ်လို့ရပါပြီခင်ဗျာ "
        "အားလုံးကိုကျေးဇူးတင်ပါသည်\n\n"
        "🔗 *TikTok video link တစ်ခု ပို့ပေးပါဗျာ။*"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# =========================================================
# Receive TikTok URL
# =========================================================

async def receive_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    match = TIKTOK_REGEX.search(text)

    if not match:
        await update.message.reply_text(
            "❌ TikTok link မတွေ့ပါဘူး။\n\n"
            "ဥပမာ:\n"
            "https://www.tiktok.com/@user/video/123..."
        )
        return

    raw_url = match.group(0)
    if not raw_url.startswith("http"):
        raw_url = "https://" + raw_url

    status = await update.message.reply_text(
        "🔎 TikTok Video ကို စစ်ဆေးနေပါတယ်...\n⏳ ခဏစောင့်ပါ..."
    )

    try:
        # Link အတိုကို Real Link သို့ ပြောင်းလဲခြင်း
        url = await asyncio.to_thread(unshorten_url, raw_url)
        info = await asyncio.to_thread(get_video_info, url)
        title = info.get("title") or "TikTok Video"

        user_jobs[update.effective_user.id] = {
            "url": url,
            "title": title,
        }

        keyboard = [
            [
                InlineKeyboardButton(
                    "🔥 Best Quality", callback_data="quality_best"
                )
            ],
            [
                InlineKeyboardButton("🎥 720p", callback_data="quality_720"),
                InlineKeyboardButton("🎥 480p", callback_data="quality_480"),
            ],
            [
                InlineKeyboardButton("📱 360p", callback_data="quality_360"),
            ],
        ]

        await status.edit_text(
            f"🎬 *Video Found!*\n\n📝 `{title[:150]}`\n\n👇 Download Quality ရွေးပါ",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    except Exception as e:
        await status.edit_text(
            "❌ Video information ရယူလို့မရပါဘူး။\n\nTikTok link"
            " မှန်မမှန် စစ်ကြည့်ပါ။"
        )
        print("INFO ERROR:", e)

# =========================================================
# Get TikTok information
# =========================================================

def get_video_info(url):
    options = COMMON_YTDLP_OPTIONS.copy()
    options.update({
        "skip_download": True,
        "noplaylist": True,
    })

    with yt_dlp.YoutubeDL(options) as ydl:
        return ydl.extract_info(url, download=False)

# =========================================================
# Quality button
# =========================================================

async def quality_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id not in user_jobs:
        await query.edit_message_text(
            "⚠️ ဒီ download session မရှိတော့ပါဘူး။\nTikTok link အသစ် ပြန်ပို့ပါ။"
        )
        return

    quality = query.data.replace("quality_", "")
    url = user_jobs[user_id]["url"]

    quality_names = {
        "best": "🔥 Best Quality",
        "720": "🎥 720p",
        "480": "🎥 480p",
        "360": "📱 360p",
    }

    selected = quality_names.get(quality, "Best Quality")

    await query.edit_message_text(
        f"✅ Quality: {selected}\n\n🔗 TikTok Video ကို download"
        " လုပ်နေပါတယ်...\n\n◐ Preparing..."
    )

    try:
        await download_video(query, url, quality)
    except Exception as e:
        print("DOWNLOAD ERROR:", e)
        await query.edit_message_text(
            "❌ Download မအောင်မြင်ပါဘူး။\n\nဒီ TikTok video ကို download"
            " မရနိုင်တာ သို့မဟုတ် format ပြဿနာ ဖြစ်နိုင်ပါတယ်။"
        )
    finally:
        user_jobs.pop(user_id, None)

# =========================================================
# Download
# =========================================================

async def download_video(query, url, quality):
    chat_id = query.message.chat_id
    folder = DOWNLOAD_DIR / str(chat_id)
    folder.mkdir(parents=True, exist_ok=True)

    output_template = str(folder / "%(id)s.%(ext)s")
    progress_message = query.message

    spinner = ["◐", "◓", "◑", "◒"]
    progress_state = {
        "percent": 0,
        "speed": "",
        "eta": "",
        "last_update": 0,
    }

    if quality == "best":
        format_selector = "bestvideo+bestaudio/best"
    else:
        height = int(quality)
        format_selector = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"

    def progress_hook(data):
        if data["status"] == "downloading":
            total = data.get("total_bytes") or data.get("total_bytes_estimate")
            downloaded = data.get("downloaded_bytes", 0)
            if total:
                percent = int(downloaded / total * 100)
                progress_state["percent"] = percent
            progress_state["speed"] = data.get("_speed_str") or ""
            progress_state["eta"] = data.get("_eta_str") or ""
        elif data["status"] == "finished":
            progress_state["percent"] = 100

    options = COMMON_YTDLP_OPTIONS.copy()
    options.update({
        "format": format_selector,
        "outtmpl": output_template,
        "merge_output_format": "mp4",
        "noplaylist": True,
        "progress_hooks": [progress_hook],
        "retries": 10,
        "fragment_retries": 10,
    })

    loop = asyncio.get_running_loop()
    download_task = loop.run_in_executor(
        None, lambda: run_download(url, options)
    )

    frame = 0
    while not download_task.done():
        percent = progress_state["percent"]
        speed = progress_state["speed"]
        eta = progress_state["eta"]
        bar_length = 12

        filled = int(bar_length * percent / 100)
        bar = "━" * filled + "░" * (bar_length - filled)
        icon = spinner[frame % len(spinner)]

        text = (
            f"{icon} *Downloading TikTok...*\n\n"
            f"{bar} `{percent}%`\n\n"
            f"⚡ Speed: `{speed or 'calculating...'}`\n"
            f"⏱ ETA: `{eta or 'calculating...'}`\n\n"
            f"🎯 Quality: `{quality}p`"
            if quality != "best"
            else (
                f"{icon} *Downloading TikTok...*\n\n"
                f"{bar} `{percent}%`\n\n"
                f"⚡ Speed: `{speed or 'calculating...'}`\n"
                f"⏱ ETA: `{eta or 'calculating...'}`\n\n"
                f"🔥 Quality: `BEST`"
            )
        )

        try:
            await progress_message.edit_text(text, parse_mode="Markdown")
        except Exception:
            pass

        frame += 1
        await asyncio.sleep(1.2)

    await download_task

    files = list(folder.glob("*"))
    video_files = [
        f
        for f in files
        if f.suffix.lower() in [".mp4", ".mkv", ".webm", ".mov"]
    ]

    if not video_files:
        raise RuntimeError("Downloaded video not found")

    video = max(video_files, key=lambda f: f.stat().st_mtime)

    await progress_message.edit_text(
        "✅ *Download Complete!*\n\n📤 Telegram ထဲကို video ပို့နေပါတယ်...\n◐"
        " Uploading...",
        parse_mode="Markdown",
    )

    await progress_message.get_bot().send_chat_action(
        chat_id=chat_id, action=ChatAction.UPLOAD_VIDEO
    )

    caption = "🎬 *TikTok Downloaded*\n\n✨ Created by AungSoeOo"

    with open(video, "rb") as file:
        await progress_message.get_bot().send_video(
            chat_id=chat_id,
            video=file,
            caption=caption,
            parse_mode="Markdown",
            supports_streaming=True,
        )

    try:
        for file in folder.glob("*"):
            file.unlink(missing_ok=True)
        folder.rmdir()
    except Exception:
        pass

    await progress_message.delete()

def run_download(url, options):
    with yt_dlp.YoutubeDL(options) as ydl:
        return ydl.download([url])

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print("BOT ERROR:", context.error)

def main():
    if not BOT_TOKEN or BOT_TOKEN == "PUT_YOUR_NEW_TOKEN_HERE":
        print("\n❌ BOT_TOKEN မထည့်ရသေးပါဘူး။\n")
        return

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        CallbackQueryHandler(quality_callback, pattern=r"^quality_")
    )
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, receive_link)
    )
    app.add_error_handler(error_handler)

    print("🚀 TikTok Downloader Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
