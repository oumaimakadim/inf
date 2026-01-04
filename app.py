import streamlit as st
import asyncio
import edge_tts
import os
from gradio_client import Client, handle_file
import tempfile

# Page Config
st.set_page_config(page_title="AI Video Free (HuggingFace)", page_icon="🎥")

st.title("🎥 AI Talking Head (Fabor Edition)")
st.caption("هاد النسخة مجانية باستعمال سيرفرات Hugging Face")

# --- FUNCTIONS ---

async def generate_audio_edge(text, voice="en-US-AriaNeural"):
    """توليد الصوت فابور باستعمال EdgeTTS"""
    output_file = "temp_audio.mp3"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)
    return output_file

def generate_video_free(image_path, audio_path):
    """توليد الفيديو باستعمال سيرفرات Hugging Face فابور"""
    try:
        # هاد السيرفر كيكون عليه الضغط بعض المرات، إلا ما خدمش نقدر نعطيك واحد آخر
        client = Client("vinthony/SadTalker") 
        
        result = client.predict(
            source_image=handle_file(image_path),
            driven_audio=handle_file(audio_path),
            preprocess="full",     # 'crop', 'resize', 'full'
            still=True,            # واش يبقى الراس ثابت
            enhancer="gfpgan",      # كايحسن جودة الوجه
            batch_size=1,
            size=256,              # الجودة (256 أو 512)
            api_name="/predict"
        )
        # النتيجة كتكون عبارة عن مسار فيديو مؤقت
        return result
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# --- UI ---

col1, col2 = st.columns(2)

with col1:
    uploaded_image = st.file_uploader("Upload Image", type=['jpg', 'png', 'jpeg'])
    if uploaded_image:
        st.image(uploaded_image, width=250)
        with open("temp_image.jpg", "wb") as f:
            f.write(uploaded_image.getbuffer())

    text_input = st.text_area("Script", "Hello friend, this is free!")

with col2:
    if st.button("🎬 Generate Free Video"):
        if not uploaded_image or not text_input:
            st.warning("Please provide image and text.")
        else:
            with st.status("Working...", expanded=True) as status:
                # 1. Audio
                st.write("🎙️ Generating Audio...")
                audio_path = asyncio.run(generate_audio_edge(text_input))
                
                # 2. Video (Hugging Face)
                st.write("🚀 Sending to Free GPU Server (Might take a minute)...")
                video_path = generate_video_free("temp_image.jpg", audio_path)
                
                if video_path:
                    status.update(label="✅ Success!", state="complete")
                    # فيديو النتيجة غالبا كيكون داخل ملف مضغوط أو مسار
                    # Hugging Face كيعطي مسار mp4 مباشرة
                    st.video(video_path)
                    st.success("تم توليد الفيديو بنجاح وفابور!")
                else:
                    status.update(label="❌ Failed", state="error")
                    st.info("ملاحظة: السيرفرات الفابور كيكون عليها الزحام، جرب مرة أخرى مورا شوية.")

# تنظيف الملفات المؤقتة (اختياري)