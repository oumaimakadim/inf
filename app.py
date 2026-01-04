"""
Main Streamlit application for video generation.
Orchestrates the entire pipeline from user inputs to final video.
"""

import os
import sys
import streamlit as st
import tempfile
import shutil
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.config import TEMP_DIR, AUTO_CLEANUP
from utils.model_downloader import setup_all
from modules.tts_generator import TTSGenerator
from modules.background_generator import BackgroundGenerator
from modules.lip_sync import LipSyncGenerator
from modules.person_animator import PersonAnimator
from modules.video_composer import VideoComposer


# Page configuration
st.set_page_config(
    page_title="AI Video Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.75rem;
        border-radius: 0.5rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        color: #155724;
    }
    </style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'setup_complete' not in st.session_state:
        st.session_state.setup_complete = False
    if 'generators_initialized' not in st.session_state:
        st.session_state.generators_initialized = False
    if 'generated_video' not in st.session_state:
        st.session_state.generated_video = None


def run_setup():
    """Run initial setup for models and dependencies."""
    with st.spinner("🔧 Running initial setup... This may take a while on first run."):
        setup_success = setup_all()
        
        if setup_success:
            st.session_state.setup_complete = True
            st.success("✅ Setup completed successfully!")
        else:
            st.error("❌ Setup failed. Please check the console for errors.")
            st.stop()


def initialize_generators():
    """Initialize all generator modules."""
    if not st.session_state.generators_initialized:
        with st.spinner("🚀 Initializing AI models..."):
            try:
                st.session_state.tts_generator = TTSGenerator()
                st.session_state.bg_generator = BackgroundGenerator()
                st.session_state.lip_sync_generator = LipSyncGenerator()
                st.session_state.animator = PersonAnimator()
                st.session_state.composer = VideoComposer()
                
                st.session_state.generators_initialized = True
                st.success("✅ All models initialized!")
            except Exception as e:
                st.error(f"❌ Failed to initialize models: {e}")
                st.stop()


def generate_video(image_file, text_input, scenario_description):
    """
    Main video generation pipeline.
    
    Args:
        image_file: Uploaded image file
        text_input: Text to be spoken
        scenario_description: Video scenario description
    
    Returns:
        str: Path to generated video
    """
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Create temporary directory for this session
        session_temp = os.path.join(TEMP_DIR, f"session_{os.getpid()}")
        os.makedirs(session_temp, exist_ok=True)
        
        # Step 1: Save uploaded image
        status_text.text("📸 Processing input image...")
        progress_bar.progress(10)
        
        image_path = os.path.join(session_temp, "input_image.jpg")
        with open(image_path, "wb") as f:
            f.write(image_file.getbuffer())
        
        # Step 2: Generate speech from text
        status_text.text("🎙️ Generating speech from text...")
        progress_bar.progress(20)
        
        audio_path = st.session_state.tts_generator.generate_speech(
            text_input,
            os.path.join(session_temp, "speech.wav")
        )
        
        # Step 3: Generate background image
        status_text.text("🎨 Generating background scene...")
        progress_bar.progress(35)
        
        background_path = st.session_state.bg_generator.generate_background(
            scenario_description,
            os.path.join(session_temp, "background.png"),
            num_inference_steps=25  # Reduced for faster generation
        )
        
        # Step 4: Create lip-synced talking head
        status_text.text("👄 Synchronizing lips with speech...")
        progress_bar.progress(50)
        
        talking_head_path = st.session_state.lip_sync_generator.generate_lip_sync(
            image_path,
            audio_path,
            os.path.join(session_temp, "talking_head.mp4")
        )
        
        # Step 5: Compose final video
        status_text.text("🎬 Composing final video...")
        progress_bar.progress(75)
        
        final_video_path = st.session_state.composer.compose_video(
            talking_head_path,
            background_path,
            os.path.join(session_temp, "final_video.mp4")
        )
        
        # Step 6: Complete
        status_text.text("✅ Video generation complete!")
        progress_bar.progress(100)
        
        return final_video_path
        
    except Exception as e:
        status_text.text(f"❌ Error: {str(e)}")
        st.error(f"Video generation failed: {e}")
        raise


def main():
    """Main application function."""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🎬 AI Video Generator</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("ℹ️ About")
        st.write("""
        This app generates videos from:
        - 📸 An image of a person
        - 📝 Text to be spoken
        - 🎨 A scenario description
        
        **Features:**
        - Text-to-Speech (Coqui TTS)
        - Lip Synchronization (Wav2Lip)
        - Background Generation (Stable Diffusion)
        - Video Composition (MoviePy)
        """)
        
        st.markdown("---")
        
        st.header("⚙️ Settings")
        
        if st.button("🔧 Run Setup"):
            run_setup()
        
        if st.session_state.setup_complete:
            st.success("✅ Setup Complete")
        
        st.markdown("---")
        st.caption("Built with ❤️ using free, open-source tools")
    
    # Main content
    if not st.session_state.setup_complete:
        st.info("👈 Please run setup from the sidebar to get started.")
        st.stop()
    
    # Initialize generators
    initialize_generators()
    
    # Input section
    st.header("📥 Input")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1️⃣ Upload Image")
        image_file = st.file_uploader(
            "Choose an image of a person",
            type=["jpg", "jpeg", "png"],
            help="Upload a clear photo of a person's face"
        )
        
        if image_file:
            st.image(image_file, caption="Uploaded Image", use_container_width=True)
    
    with col2:
        st.subheader("2️⃣ Enter Text")
        text_input = st.text_area(
            "Text to be spoken",
            height=150,
            placeholder="Enter the dialogue or script here...",
            help="This text will be converted to speech and lip-synced"
        )
        
        st.subheader("3️⃣ Describe Scenario")
        scenario_description = st.text_area(
            "Video scenario description",
            height=100,
            placeholder="e.g., A person walking through a forest while talking about adventure",
            help="Describe the background scene and overall video narrative"
        )
    
    # Generate button
    st.markdown("---")
    
    if st.button("🎬 Generate Video", type="primary"):
        # Validation
        if not image_file:
            st.error("❌ Please upload an image")
            st.stop()
        
        if not text_input or not text_input.strip():
            st.error("❌ Please enter text to be spoken")
            st.stop()
        
        if not scenario_description or not scenario_description.strip():
            st.error("❌ Please describe the video scenario")
            st.stop()
        
        # Generate video
        st.markdown("---")
        st.header("🎥 Generation Progress")
        
        try:
            video_path = generate_video(image_file, text_input, scenario_description)
            st.session_state.generated_video = video_path
            
        except Exception as e:
            st.error(f"Generation failed: {e}")
            st.stop()
    
    # Display result
    if st.session_state.generated_video:
        st.markdown("---")
        st.header("🎉 Result")
        
        # Display video
        st.video(st.session_state.generated_video)
        
        # Download button
        with open(st.session_state.generated_video, "rb") as f:
            video_bytes = f.read()
        
        st.download_button(
            label="⬇️ Download Video",
            data=video_bytes,
            file_name="generated_video.mp4",
            mime="video/mp4"
        )
        
        st.success("✅ Video generated successfully!")
        
        # Option to generate another
        if st.button("🔄 Generate Another Video"):
            st.session_state.generated_video = None
            st.rerun()


if __name__ == "__main__":
    main()
