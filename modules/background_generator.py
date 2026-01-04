"""
Background image generation using Stable Diffusion.
Generates scene backgrounds based on text descriptions.
"""

import os
import torch
from PIL import Image
from utils.config import SD_MODEL_ID, SD_MODEL_CACHE, DEVICE, TEMP_DIR


class BackgroundGenerator:
    """Generate background images using Stable Diffusion."""
    
    def __init__(self):
        self.pipe = None
        self._initialize_pipeline()
    
    def _initialize_pipeline(self):
        """Initialize Stable Diffusion pipeline."""
        try:
            from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
            
            print(f"[BG] Initializing Stable Diffusion on {DEVICE}...")
            
            # Load pipeline
            self.pipe = StableDiffusionPipeline.from_pretrained(
                SD_MODEL_ID,
                torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
                cache_dir=SD_MODEL_CACHE,
                safety_checker=None,  # Disable safety checker for speed
            )
            
            # Use faster scheduler
            self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipe.scheduler.config
            )
            
            # Move to device
            self.pipe = self.pipe.to(DEVICE)
            
            # Enable memory optimizations
            if DEVICE == "cuda":
                self.pipe.enable_attention_slicing()
                # Try to enable xformers if available
                try:
                    self.pipe.enable_xformers_memory_efficient_attention()
                    print("[BG] xformers memory optimization enabled")
                except Exception:
                    print("[BG] xformers not available, using default attention")
            
            print("[BG] Stable Diffusion initialized successfully")
            
        except Exception as e:
            print(f"[BG] Failed to initialize Stable Diffusion: {e}")
            raise
    
    def generate_background(self, prompt, output_path=None, width=1280, height=720, 
                          num_inference_steps=30, guidance_scale=7.5):
        """
        Generate a background image from text prompt.
        
        Args:
            prompt (str): Text description of the background scene
            output_path (str, optional): Path to save image
            width (int): Image width (default: 1280)
            height (int): Image height (default: 720)
            num_inference_steps (int): Number of denoising steps (default: 30)
            guidance_scale (float): Guidance scale for generation (default: 7.5)
        
        Returns:
            str: Path to generated image
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        # Create output path if not provided
        if output_path is None:
            output_path = os.path.join(TEMP_DIR, f"background_{os.getpid()}.png")
        
        print(f"[BG] Generating background image...")
        print(f"[BG] Prompt: {prompt}")
        print(f"[BG] Resolution: {width}x{height}")
        print(f"[BG] Steps: {num_inference_steps}")
        
        try:
            # Enhance prompt for better backgrounds
            enhanced_prompt = f"{prompt}, high quality, detailed, cinematic lighting, 8k"
            
            # Generate image
            with torch.inference_mode():
                result = self.pipe(
                    prompt=enhanced_prompt,
                    width=width,
                    height=height,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                )
            
            # Save image
            image = result.images[0]
            image.save(output_path)
            
            if not os.path.exists(output_path):
                raise RuntimeError("Background generation failed - output file not created")
            
            file_size = os.path.getsize(output_path)
            print(f"[BG] Background generated successfully: {output_path} ({file_size} bytes)")
            
            return output_path
            
        except Exception as e:
            print(f"[BG] Error generating background: {e}")
            raise
    
    def generate_multiple_backgrounds(self, prompts, output_dir=None, **kwargs):
        """
        Generate multiple background images from a list of prompts.
        
        Args:
            prompts (list): List of text prompts
            output_dir (str, optional): Directory to save images
            **kwargs: Additional arguments for generate_background
        
        Returns:
            list: Paths to generated images
        """
        if output_dir is None:
            output_dir = TEMP_DIR
        
        os.makedirs(output_dir, exist_ok=True)
        
        generated_images = []
        for i, prompt in enumerate(prompts):
            output_path = os.path.join(output_dir, f"background_{i+1}.png")
            try:
                image_path = self.generate_background(prompt, output_path, **kwargs)
                generated_images.append(image_path)
            except Exception as e:
                print(f"[BG] Failed to generate background {i+1}: {e}")
                # Continue with other images
        
        return generated_images


def generate_background(prompt, output_path=None, **kwargs):
    """
    Convenience function to generate a single background.
    
    Args:
        prompt (str): Text description of the scene
        output_path (str, optional): Output file path
        **kwargs: Additional generation parameters
    
    Returns:
        str: Path to generated image
    """
    generator = BackgroundGenerator()
    return generator.generate_background(prompt, output_path, **kwargs)


if __name__ == "__main__":
    # Test the background generator
    test_prompt = "A beautiful forest with sunlight filtering through trees"
    output = generate_background(test_prompt, num_inference_steps=20)
    print(f"Test background generated: {output}")
