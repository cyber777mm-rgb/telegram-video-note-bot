import os
import subprocess
import tempfile

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.environ["BOT_TOKEN"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ဟေး 👋 Video ပို့လိုက်နော်။\n"
        "Telegram Video Note ⭕ အဖြစ် ပြောင်းပေးမယ် 😎"
    )


async def convert_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message or not message.video:
        return

    status = await message.reply_text("⏳ Video Note ပြောင်းနေပါတယ်...")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = os.path.join(temp_dir, "input.mp4")
            output_path = os.path.join(temp_dir, "output.mp4")

            telegram_file = await context.bot.get_file(message.video.file_id)
            await telegram_file.download_to_drive(input_path)

            command = [
                "ffmpeg",
                "-y",
                "-i", input_path,
                "-vf",
                "crop='min(iw,ih)':'min(iw,ih)',scale=640:640",
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-crf", "25",
                "-c:a", "aac",
                "-b:a", "96k",
                "-movflags", "+faststart",
                output_path,
            ]

            subprocess.run(
                command,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            with open(output_path, "rb") as video_note:
                await context.bot.send_video_note(
                    chat_id=message.chat_id,
                    video_note=video_note,
                    length=640,
                )

            await status.delete()

    except Exception as e:
        print("VIDEO NOTE ERROR:", repr(e))
        await status.edit_text(
            "❌ Video Note ပြောင်းလို့မရသေးဘူး။\n"
            f"Error: {str(e)[:800]}"
        )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.VIDEO,
            convert_video,
        )
    )

    app.run_polling()


if __name__ == "__main__":
    main()
