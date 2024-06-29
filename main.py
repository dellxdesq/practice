from parser import get_transcript, merge_transcripts, format_time
from database import VideoTranscriptDB, VideoTranscriptQuery

def main():
    video_url = input("Введите URL видео на YouTube: ")

    db = VideoTranscriptDB()
    video_id = db.insert_video(video_url)

    if video_id is None:
        print("Это видео уже есть в базе данных.")
        return

    transcript = get_transcript(video_url)

    if transcript:
        merged_transcript = merge_transcripts(transcript)

        for entry in merged_transcript:
            start_time = format_time(entry['start'])
            text = entry['text']
            db.insert_segment(video_id, start_time, text)
            print(f"{start_time}: {text}")
    else:
        print("Расшифровка на русском языке недоступна для данного видео.")

def query_segments():
    video_url = input("Введите URL видео для запроса сегментов: ")

    query = VideoTranscriptQuery()
    segments = query.get_segments_by_url(video_url)

    if segments:
        for start_time, text in segments:
            print(f"{start_time}: {text}")
    else:
        print("Видео не найдено в базе данных.")

if __name__ == "__main__":
    while True:
        choice = input("Введите '1' для добавления видео или '2' для запроса сегментов: ")
        if choice == '1':
            main()
        elif choice == '2':
            query_segments()
        else:
            print("Неверный ввод. Попробуйте снова.")
