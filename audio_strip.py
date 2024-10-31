import streamlit as st
from moviepy.editor import VideoFileClip
import tempfile
import os
from openai import OpenAI

# Set your OpenAI API key directly
api_key = ""  # Replace with your actual API key
client = OpenAI(api_key=api_key)

# Function to extract audio from video
def extract_audio(video_file, output_format="mp3"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{output_format}") as temp_audio_file:
        video = VideoFileClip(video_file)
        audio = video.audio
        audio.write_audiofile(temp_audio_file.name)
        audio.close()
        video.close()
        return temp_audio_file.name

# Function to transcribe audio using Whisper API
def transcribe_audio(audio_path):
    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcript.text  # Access the text attribute directly

# Function to summarize transcription using Chat API
def summarize_transcription(transcription_text):
    completion = client.chat.completions.create(
        model="gpt-4",  # Use the appropriate model
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Summarize the following text: {transcription_text}"}
        ]
    )
    return completion.choices[0].message.content  # Access the summary content correctly

# Streamlit UI
st.title("Video/Audio Transcriber")

# File uploader for video files
uploaded_video = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov", "mkv"])
# File uploader for MP3 files
uploaded_audio = st.file_uploader("Or upload an MP3 file", type=["mp3"])

# Initialize variable for temporary file paths
temp_video_file_path = None
output_audio_path = None
temp_audio_file_path = None

# Process the uploaded file
if uploaded_video is not None:
    # Save the uploaded video file to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
        temp_video_file.write(uploaded_video.read())
        temp_video_file_path = temp_video_file.name

    # Extract the audio and transcribe it
    output_audio_path = extract_audio(temp_video_file_path)
    transcription_text = transcribe_audio(output_audio_path)

elif uploaded_audio is not None:
    # Save the uploaded MP3 file to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
        temp_audio_file.write(uploaded_audio.read())
        temp_audio_file_path = temp_audio_file.name

    # Transcribe the MP3 audio directly
    transcription_text = transcribe_audio(temp_audio_file_path)

else:
    transcription_text = None

# Display transcription and summary if available
if transcription_text:
    st.write("Transcription:")
    st.write(transcription_text)

    # Summarize the transcription
    summary_text = summarize_transcription(transcription_text)

    # Display summary
    st.write("Summary:")
    st.write(summary_text)

    # Optionally, provide audio download button
    if uploaded_video is not None:
        with open(output_audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read()

        st.download_button(
            label="Download Audio",
            data=audio_bytes,
            file_name="extracted_audio.mp3",
            mime="audio/mp3"
        )

# Clean up temporary files
if temp_video_file_path and os.path.exists(temp_video_file_path):
    os.remove(temp_video_file_path)

if output_audio_path and os.path.exists(output_audio_path):
    os.remove(output_audio_path)

if temp_audio_file_path and os.path.exists(temp_audio_file_path):
    os.remove(temp_audio_file_path)
