from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from parser import get_transcript, merge_transcripts, format_time
from database import VideoTranscriptDB, VideoTranscriptQuery

class YouTubeTranscriptBot:
    def __init__(self, token: str):
        self.application = Application.builder().token(token).build()

        self.db = VideoTranscriptDB()

        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("add", self.add_video))
        self.application.add_handler(CommandHandler("query", self.query_segments))

    async def start(self, update: Update, context: CallbackContext):
        await update.message.reply_text("Привет! Я бот для работы с расшифровками видео на YouTube. Используйте /add для добавления видео и /query для запроса сегментов.")

    async def add_video(self, update: Update, context: CallbackContext):
        if not context.args:
            await update.message.reply_text("Пожалуйста, введите URL видео. Пример: /add https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            return

        video_url = context.args[0]
        video_id = self.db.insert_video(video_url)

        if video_id is None:
            await update.message.reply_text("Это видео уже есть в базе данных.")
            return

        transcript = get_transcript(video_url)
        if transcript:
            merged_transcript = merge_transcripts(transcript)

            for entry in merged_transcript:
                start_time = format_time(entry['start'])
                text = entry['text']
                self.db.insert_segment(video_id, start_time, text)
                await update.message.reply_text(f"{start_time}: {text}")
        else:
            await update.message.reply_text("Расшифровка на русском языке недоступна для данного видео.")

    async def query_segments(self, update: Update, context: CallbackContext):
        if not context.args:
            await update.message.reply_text("Пожалуйста, введите URL видео. Пример: /query https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            return

        video_url = context.args[0]
        query = VideoTranscriptQuery()
        segments = query.get_segments_by_url(video_url)

        if segments:
            for start_time, text in segments:
                await update.message.reply_text(f"{start_time}: {text}")
        else:
            await update.message.reply_text("Видео не найдено в базе данных.")

    def run(self):
        self.application.run_polling()

if __name__ == "__main__":
    TOKEN = ""
    bot = YouTubeTranscriptBot(TOKEN)
    bot.run()
