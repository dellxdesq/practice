import re
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from urllib.parse import urlparse, parse_qs

def get_video_id(url):
    query = urlparse(url).query
    params = parse_qs(query)

    if 'v' in params:
        return params['v'][0]
    else:
        # Try to extract video ID using regular expression as a fallback
        match = re.search(r"(?:v=|\/)([a-zA-Z0-9_-]{11})", url)
        if match:
            return match.group(1)
        else:
            raise ValueError("Не удалось извлечь идентификатор видео из URL")

def get_transcript(video_url):
    video_id = get_video_id(video_url)

    try:
        # Try to get transcript in Russian
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ru'])
        return transcript
    except TranscriptsDisabled:
        print(f"Transcripts are disabled for this video: {video_url}")
    except NoTranscriptFound as e:
        print(f"No transcript found for video {video_url} in Russian.")
        print("Available languages:", e.available_transcripts)
    except VideoUnavailable:
        print(f"The video is unavailable: {video_url}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def merge_transcripts(transcript, max_duration=60.0):
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
            temp_start = entry['start'] + entry['duration']  # Start a new segment here
            temp_duration = 0.0
    if temp_text:  # Add the remaining text
        merged_transcript.append({
            'start': temp_start,
            'text': temp_text.strip()
        })
    return merged_transcript

def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    if minutes > 0:
        return f"{minutes}м {seconds}с"
    else:
        return f"{seconds}с"
