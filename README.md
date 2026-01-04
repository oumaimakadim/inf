# AI Video Generator 🎬

A complete Streamlit web application that generates videos from images, text, and scenario descriptions using free, open-source AI tools.

## Features

- 🎙️ **Text-to-Speech**: Convert text to natural speech using Coqui TTS
- 👄 **Lip Synchronization**: Create realistic talking head videos with Wav2Lip
- 🎨 **Background Generation**: Generate scene backgrounds using Stable Diffusion
- 🎬 **Video Composition**: Combine all elements into a polished final video with MoviePy

## Requirements

### Hardware
- **Recommended**: CUDA-compatible GPU with 6GB+ VRAM
- **Minimum**: 8GB RAM, 16GB+ recommended
- **Disk Space**: ~15GB for models and dependencies

### Software
- Python 3.8-3.10 (3.11+ may have compatibility issues with Wav2Lip)
- FFmpeg
- Git

## Installation

### Quick Start (Linux/macOS)

```bash
# Clone or navigate to the project directory
cd /home/oumaima/Desktop/inf

# Run setup script
chmod +x setup.sh
./setup.sh
```

### Manual Installation

1. **Install system dependencies**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install ffmpeg git
   
   # macOS
   brew install ffmpeg git
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup models**:
   ```bash
   python utils/model_downloader.py
   ```

## Usage

1. **Activate virtual environment**:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Run the application**:
   ```bash
   streamlit run app.py
   ```

3. **Open your browser** to the URL shown (usually `http://localhost:8501`)

4. **Generate videos**:
   - Click "Run Setup" in the sidebar (first time only)
   - Upload an image of a person
   - Enter the text to be spoken
   - Describe the video scenario
   - Click "Generate Video"

## Project Structure

```
inf/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── setup.sh                    # Automated setup script
├── modules/                    # Core processing modules
│   ├── tts_generator.py       # Text-to-speech
│   ├── lip_sync.py            # Lip synchronization
│   ├── background_generator.py # Background generation
│   ├── person_animator.py     # Person animation
│   └── video_composer.py      # Video composition
├── utils/                      # Utility modules
│   ├── config.py              # Configuration
│   └── model_downloader.py    # Model setup
├── models/                     # Downloaded models (created on setup)
├── temp/                       # Temporary files (created on run)
└── Wav2Lip/                   # Wav2Lip repository (cloned on setup)
```

## Technologies Used

- **Streamlit**: Web application framework
- **Coqui TTS**: Text-to-speech synthesis
- **Wav2Lip**: Lip synchronization
- **Stable Diffusion**: Background image generation
- **MoviePy**: Video editing and composition
- **OpenCV**: Image processing
- **PyTorch**: Deep learning framework

## Troubleshooting

### GPU Issues
If you encounter GPU memory errors:
- The app will automatically fall back to CPU
- Reduce Stable Diffusion inference steps in `modules/background_generator.py`
- Close other GPU-intensive applications

### Wav2Lip Errors
If Wav2Lip fails:
- Ensure Python version is 3.8-3.10
- Check that FFmpeg is installed: `ffmpeg -version`
- Verify checkpoint downloaded: `ls models/wav2lip_gan.pth`
- The app will use a fallback method if Wav2Lip fails

### Slow Performance
- First run is slow due to model downloads
- CPU processing takes 10-30 minutes per video
- GPU processing takes 2-5 minutes per video
- Reduce video quality settings in config.py

### Memory Issues
- Close other applications
- Reduce image resolution
- Use shorter text inputs
- Enable automatic cleanup in config.py

## Performance Optimization

Edit `utils/config.py` to adjust:
- Video resolution: `DEFAULT_RESOLUTION`
- FPS: `DEFAULT_FPS`
- Stable Diffusion steps: In `modules/background_generator.py`

## License

This project uses multiple open-source libraries, each with their own licenses:
- Coqui TTS: MPL 2.0
- Wav2Lip: MIT
- Stable Diffusion: CreativeML Open RAIL-M
- MoviePy: MIT
- Streamlit: Apache 2.0

## Credits

Built with:
- [Coqui TTS](https://github.com/coqui-ai/TTS)
- [Wav2Lip](https://github.com/Rudrabha/Wav2Lip)
- [Stable Diffusion](https://github.com/CompVis/stable-diffusion)
- [MoviePy](https://github.com/Zulko/moviepy)
- [Streamlit](https://streamlit.io)

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review console output for error messages
3. Ensure all dependencies are properly installed
4. Verify hardware meets minimum requirements
