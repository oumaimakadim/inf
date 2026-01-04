import replicate
import os

# Ta2kdi anaki zti REPLICATE_API_TOKEN f .env ola f Render Environment Variables

def generate_talking_head(image_path, audio_path):
    """
    Hadi kat-uploadé l-image w l-audio l Replicate,
    w katkhdm 'SadTalker' bach t-généri video.
    """
    try:
        print("[INFO] Uploading files to Replicate...")
        
        # 1. Khassna n-openiw les fichiers
        with open(image_path, "rb") as img_file, open(audio_path, "rb") as audio_file:
            
            # 2. Lansiw l-model (SadTalker)
            # Hada howa l-model li kay7rrk l-wjh
            output = replicate.run(
                "cjwbw/sadtalker:3aa3dac9353cc4d6bd62a8f95957bd844003b4184f23bc2cfbd4e3a7962ccd02",
                input={
                    "source_image": img_file,
                    "driven_audio": audio_file,
                    "enhancer": "gfpgan", # Bach l-wjh yban n9i
                    "still": True,        # Bach t-rkkz 3la l-fomm
                    "preprocess": "full"
                }
            )
        
        # Replicate kayrdd lik URL dyal l-video
        video_url = output
        print(f"[SUCCESS] Video generated: {video_url}")
        return video_url

    except Exception as e:
        print(f"[ERROR] Replicate failed: {str(e)}")
        return None