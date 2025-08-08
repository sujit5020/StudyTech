import os
import openai
import whisper
from pydub import AudioSegment

# Load API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load Whisper model once
whisper_model = whisper.load_model("base")

def transcribe_audio(audio_path):
    try:
        # Convert to .wav if necessary
        if not audio_path.endswith(".wav"):
            sound = AudioSegment.from_file(audio_path)
            audio_path = audio_path.replace(".mp3", ".wav")
            sound.export(audio_path, format="wav")

        result = whisper_model.transcribe(audio_path)
        return result['text']
    except Exception as e:
        return f"Transcription error: {str(e)}"

def get_response_from_text(user_text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI tutor."},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7,
            max_tokens=150
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Response generation error: {str(e)}"
