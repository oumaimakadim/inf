import streamlit as st
import replicate
import os
import asyncio
import edge_tts
import tempfile
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()

# Page Config
st.set_page_config(page_title="AI Video Generator (Replicate)", page_icon="🎥", layout="wide")

# Sidebar for Instructions
with st.sidebar:
    st.header("⚙️ Configuration")
    api_token = os.environ.get("REPLICATE_API_TOKEN")
    if api_token and api_token.startswith("r8_"):
        st.success("✅ Replicate API Token Detected")
    else:
        st.error("❌ Replicate Token missing! Check your .env or Render Environment Variables.")
        st.info("Get your token from: https://replicate.com/account/api-tokens")
    
    st.markdown("---")
    st.markdown("""
    **How it works:**
    1. Upload a face image (Passport style works best).
    2. Enter text to speak.
    3. The app generates audio (Free EdgeTTS).
    4. Replicate generates the video (SadTalker).
    """)

# Main Title
st.title("🎥 AI Talking Head Generator")
st.caption("Powered by Replicate API & EdgeTTS")

# --- FUNCTIONS ---

async def generate_audio_edge(text, voice="en-US-AriaNeural", output_file="temp_audio.mp3"):
    """Generates high-quality audio locally using EdgeTTS (Free)."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)
    return output_file

def generate_video_replicate(image_path, audio_path):
    """Sends files to Replicate to animate the face."""
    try:
        model_id = "lucataco/sadtalker:85c698db7c0a66d5011435d0191db323034e1da04b912a6d365833141b6a285b"
        output = replicate.run(
            model_id,
            input={
                "source_image": open(image_path, "rb"),
                "driven_audio": open(audio_path, "rb"),
                "enhancer": "gfpgan",
                "still": True,
                "preprocess": "full"
            }
        )
        return output
    except Exception as e:
        st.error(f"Replicate Error: {e}")
        return None
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1️⃣ Input Inputs")
    
    # Image Upload
    uploaded_file = st.file_uploader("Upload Image (JPG/PNG)", type=['jpg', 'png', 'jpeg'])
    if uploaded_file:
        st.image(uploaded_file, caption="Source Image", width=300)
        # Save temp image
        with open("temp_image.jpg", "wb") as f:
            f.write(uploaded_file.getbuffer())

    # Text Input
    text_input = st.text_area("Script to speak", "Hello! This is an AI generated video running on Streamlit and Replicate.")
    
    # Scenario (Optional - for future use)
    scenario = st.text_input("Scenario Description (Optional - Context only)", "A professional presentation")

with col2:
    st.subheader("2️⃣ Output")
    
    if st.button("🎬 Generate Video", type="primary"):
        if not uploaded_file or not text_input:
            st.warning("Please upload an image and enter text.")
        else:
            # Step 1: Generate Audio
            with st.status("Processing...", expanded=True) as status:
                st.write("🎙️ Generating Audio (EdgeTTS)...")
                audio_file = "temp_audio.mp3"
                asyncio.run(generate_audio_edge(text_input, output_file=audio_file))
                st.audio(audio_file)
                
                # Step 2: Generate Video via Replicate
                st.write("🚀 Sending to Replicate (SadTalker Model)...")
                st.write("⏳ This usually takes 10-20 seconds...")
                
                video_url = generate_video_replicate("temp_image.jpg", audio_file)
                
                if video_url:
                    status.update(label="✅ Video Ready!", state="complete", expanded=True)
                    st.success("Video Generated Successfully!")
                    st.video(video_url)
                    st.markdown(f"[📥 Download Video]({video_url})")
                else:
                    status.update(label="❌ Failed", state="error")

# Cleanup temp files
if os.path.exists("temp_image.jpg"):
    os.remove("temp_image.jpg")
# Note: We keep audio temporarily so the player works