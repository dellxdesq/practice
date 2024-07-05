import re
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from urllib.parse import urlparse, parse_qs

class TranscriptParser:
    def __init__(self):
        pass

    def get_video_id(self, url):
        query = urlparse(url).query
        params = parse_qs(query)

        if 'v' in params:
            return params['v'][0]
        else:
            match = re.search(r"(?:v=|\/)([a-zA-Z0-9_-]{11})", url)
            if match:
                return match.group(1)
            else:
                raise ValueError("Не удалось извлечь идентификатор видео из URL")

    def get_transcript(self, video_url):
        video_id = self.get_video_id(video_url)
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ru'])
            return transcript
        except TranscriptsDisabled:
            print(f"Субтитры отключены для этого видео: {video_url}")
        except NoTranscriptFound as e:
            print(f"Субтитры для видео {video_url} на русском языке не найдены.")
            print("Доступные языки:", e.available_transcripts)
        except VideoUnavailable:
            print(f"Видео недоступно: {video_url}")
        except Exception as e:
            print(f"Произошла ошибка: {str(e)}")

    def merge_transcripts(self, transcript, max_duration=60.0):
        if not transcript:
            return []

        merged_transcript = []
        temp_text = ""
        temp_start = transcript[0]['start']
        temp_duration = 0.0
        for entry in transcript:
            temp_text += " " + entry['text']
            temp_duration += entry['duration']
            if temp_duration >= max_duration:
                merged_transcript.append({
                    'start': temp_start,
                    'text': temp_text.strip()
                })
                temp_text = ""
                temp_start = entry['start']
                temp_duration = entry['duration']
        if temp_text:
            merged_transcript.append({
                'start': temp_start,
                'text': temp_text.strip()
            })
        return merged_transcript

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        if minutes > 0:
            return f"{minutes}м {seconds}с"
        else:
            return f"{seconds}с"
