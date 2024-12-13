import streamlit as st
from pytube import YouTube
from gtts import gTTS
import os
from pydub import AudioSegment
import re
import requests
import tempfile
import openai

# Title and Introduction
st.title("YouTube Video to Podcast-like Conversation")
st.markdown("### Convert YouTube videos into podcast-style conversations")

# Input Section
video_url = st.text_input("Enter YouTube Video URL")
if video_url:
    # Extract video ID from the URL using regex for robust parsing
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", video_url)
    video_id = match.group(1) if match else None

    if video_id:
        # Download audio from YouTube
        try:
            st.write("Downloading audio from YouTube...")
            yt = YouTube(video_url)
            audio_stream = yt.streams.filter(only_audio=True).first()
            temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            audio_stream.download(output_path=os.path.dirname(temp_audio_file.name), filename=os.path.basename(temp_audio_file.name))

            # Convert to WAV
            st.write("Converting audio to WAV format...")
            audio = AudioSegment.from_file(temp_audio_file.name)
            temp_wav_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            audio.export(temp_wav_file.name, format="wav")

            # Transcribe audio using OpenAI Whisper API
            st.write("Transcribing audio using Whisper API...")
            with open(temp_wav_file.name, "rb") as audio_file:
                response = openai.Audio.transcribe("whisper-1", audio_file)

            transcript = response["text"]
            st.write("### Transcript:")
            st.text_area("Transcript", transcript, height=200)

            # Generate podcast-like conversation
            st.write("### Generate Podcast")
            host_intro = "Welcome to today's podcast. Let's discuss some interesting insights from the video."
            guest_intro = "Thank you for having me. Here's what we have."

            conversation = f"Host: {host_intro}\nGuest: {guest_intro}\n{chr(10).join(['Host: What do you think about this part?\nGuest: ' + line for line in transcript.split('. ')])}"

            st.text_area("Generated Conversation", conversation, height=300)

            if st.button("Generate Audio File"):
                # Create audio
                tts = gTTS(conversation, lang='en')
                tts.save("output.mp3")

                # Convert MP3 to WAV
                sound = AudioSegment.from_mp3("output.mp3")
                sound.export("output.wav", format="wav")

                st.audio("output.wav", format="audio/wav")
                st.success("Audio file generated successfully!")

                # Clean up
                os.remove("output.mp3")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.error("Invalid YouTube URL. Please ensure you have entered a valid URL.")

# Footer
st.markdown("---")
st.markdown("Developed with ❤️ using Streamlit")
