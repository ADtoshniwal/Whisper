from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pytube import YouTube
from moviepy.editor import *
import openai
import textwrap
import os
from pydantic import BaseModel
from dotenv import load_dotenv


load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  
)

openai.api_key = os.getenv("OPENAI_API_KEY")

class POST_DATA(BaseModel):
    url: str

@app.post("/extract")
async def extract_summary(data: POST_DATA):
    try:
        # Download YouTube video
        audio_path = './download/audio.mp3'
        download_path = './download/'
        download_youtube_video(data.url, download_path)

        # Extracting audio from the video
        video_path = find_first_mp4(download_path)
        extract_audio_from_video(video_path, audio_path)

        # Converting audio to text using Whisper model
        text = audio_to_text_whisper(audio_path)

        # Summarize text using OpenAI ChatGPT
        summary = summarize_text_chatgpt(text)

        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def download_youtube_video(url, output_path):
    yt = YouTube(url)
    video = yt.streams.filter(file_extension='mp4').first()
    video.download(output_path)

def extract_audio_from_video(video_path, audio_path):
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(audio_path)

def find_first_mp4(folder_path):
    files = os.listdir(folder_path)
    for file in files:
        if file.endswith('.mp4'):
            return os.path.join(folder_path, file)
    return None

def audio_to_text_whisper(audio_path):
    print("Calling trascribe from whisper...")
    with open(audio_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript["text"]

def chunk_text(text, max_chars):
    return textwrap.wrap(text, width=max_chars)

def summarize_chunk(part, total_part, chunk):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are ChatGPT, a large language model trained by OpenAI. Answer as concisely as possible. You specialize in taking text from youtube video in multiple part return a summary of each one. generate all this in marathi also"},
            {"role": "user", "content": f"Summarize chunk Part {part}/{total_part} text: {chunk}"}
        ]
    )
    summary = response['choices'][0]['message']['content']
    return summary

def summarize_text_chatgpt(text):
    max_chars = 2048  # Adjust this value according to your needs, keeping in mind the 4000 token limit
    text_chunks = chunk_text(text, max_chars)
    chunk_count = len(text_chunks)
    messages = [{"role": "system",
                 "content": "You are ChatGPT, a large language model trained by OpenAI. Answer as concisely as possible. You specialize in taking text from youtube video in as a summary of all its chunks and return a summary at the end.generate all this in marathi also "}]

    summarized_text = text
    if chunk_count > 1:
        summarized_chunks = [summarize_chunk(i, chunk_count, chunk) for i, chunk in enumerate(text_chunks)]
        summarized_text = ' '.join(summarized_chunks)

    messages.append(
        {"role": "user",
         "content": f"Now, please summarize the following chunked summaries and generate 4 questions based on this passage, aligned with blooms taxonomy levels as apply, evaluate, analyze, and create. generate all this in marathi also  {summarized_text}"})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    summary = response['choices'][0]['message']['content']
    return summary

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
