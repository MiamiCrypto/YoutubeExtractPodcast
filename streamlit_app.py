import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from gtts import gTTS
import os
from pydub import AudioSegment
import re

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
        # Fetch transcript
        st.write("Fetching transcript...")
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            text = " ".join([item['text'] for item in transcript])
            st.write("### Transcript:")
            st.text_area("Transcript", text, height=200)

            # Generate podcast-like conversation
            st.write("### Generate Podcast")
            host_intro = "Welcome to today's podcast. Let's discuss some interesting insights from the video."
            guest_intro = "Thank you for having me. Here's what we have."        

            conversation = f"Host: {host_intro}\nGuest: {guest_intro}\n{chr(10).join(['Host: What do you think about this part?\nGuest: ' + line for line in text.split('. ')])}"

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
            st.error(f"Error fetching transcript: {e}")
    else:
        st.error("Invalid YouTube URL. Please ensure you have entered a valid URL.")

# Footer
st.markdown("---")
st.markdown("Developed with ❤️ using Streamlit")
