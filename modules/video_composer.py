"""
Video composition and montage module using MoviePy.
Combines all elements into a final video.
"""

import os
from moviepy.editor import (
    VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip,
    concatenate_videoclips, vfx
)
from utils.config import TEMP_DIR, TRANSITION_DURATION, DEFAULT_FPS, VIDEO_CODEC


class VideoComposer:
    """Compose final video from all generated elements."""
    
    def __init__(self):
        self.fps = DEFAULT_FPS
    
    def compose_video(self, talking_head_path, background_paths, output_path=None,
                     add_transitions=True, background_duration=None):
        """
        Compose final video from talking head and backgrounds.
        
        Args:
            talking_head_path (str): Path to lip-synced talking head video
            background_paths (list or str): Path(s) to background image(s)
            output_path (str, optional): Output video path
            add_transitions (bool): Add transitions between scenes
            background_duration (float, optional): Duration for each background
        
        Returns:
            str: Path to final composed video
        """
        if output_path is None:
            output_path = os.path.join(TEMP_DIR, f"final_video_{os.getpid()}.mp4")
        
        print(f"[COMPOSER] Composing final video...")
        print(f"[COMPOSER] Talking head: {talking_head_path}")
        
        # Ensure background_paths is a list
        if isinstance(background_paths, str):
            background_paths = [background_paths]
        
        print(f"[COMPOSER] Backgrounds: {len(background_paths)}")
        
        try:
            # Load talking head video
            talking_head = VideoFileClip(talking_head_path)
            total_duration = talking_head.duration
            
            print(f"[COMPOSER] Total duration: {total_duration:.2f}s")
            
            # If multiple backgrounds, split duration
            if len(background_paths) > 1:
                if background_duration is None:
                    background_duration = total_duration / len(background_paths)
                
                # Create video clips for each background
                clips = []
                current_time = 0
                
                for i, bg_path in enumerate(background_paths):
                    # Calculate clip duration
                    clip_duration = min(background_duration, total_duration - current_time)
                    
                    if clip_duration <= 0:
                        break
                    
                    # Create background clip
                    bg_clip = ImageClip(bg_path, duration=clip_duration)
                    bg_clip = bg_clip.resize(talking_head.size)
                    
                    # Extract corresponding segment of talking head
                    head_segment = talking_head.subclip(current_time, current_time + clip_duration)
                    
                    # Composite: background + talking head
                    composite = CompositeVideoClip([bg_clip, head_segment.set_position("center")])
                    
                    # Add fade transition
                    if add_transitions and i > 0:
                        composite = composite.crossfadein(TRANSITION_DURATION)
                    
                    clips.append(composite)
                    current_time += clip_duration
                
                # Concatenate all clips
                final_video = concatenate_videoclips(clips, method="compose")
                
            else:
                # Single background
                bg_clip = ImageClip(background_paths[0], duration=total_duration)
                bg_clip = bg_clip.resize(talking_head.size)
                
                # Composite
                final_video = CompositeVideoClip([bg_clip, talking_head.set_position("center")])
            
            # Set audio from talking head
            final_video = final_video.set_audio(talking_head.audio)
            
            # Write output
            print(f"[COMPOSER] Writing video to: {output_path}")
            final_video.write_videofile(
                output_path,
                codec=VIDEO_CODEC,
                audio_codec='aac',
                fps=self.fps,
                verbose=False,
                logger=None
            )
            
            # Clean up
            talking_head.close()
            final_video.close()
            
            file_size = os.path.getsize(output_path)
            print(f"[COMPOSER] Final video created: {output_path} ({file_size} bytes)")
            
            return output_path
            
        except Exception as e:
            print(f"[COMPOSER] Error composing video: {e}")
            raise
    
    def add_intro_outro(self, video_path, intro_text=None, outro_text=None, 
                       output_path=None):
        """
        Add intro and outro text cards to video.
        
        Args:
            video_path (str): Path to input video
            intro_text (str, optional): Intro text
            outro_text (str, optional): Outro text
            output_path (str, optional): Output video path
        
        Returns:
            str: Path to video with intro/outro
        """
        if output_path is None:
            output_path = os.path.join(TEMP_DIR, f"with_intro_outro_{os.getpid()}.mp4")
        
        try:
            from moviepy.editor import TextClip
            
            main_video = VideoFileClip(video_path)
            clips = []
            
            # Add intro
            if intro_text:
                intro = TextClip(
                    intro_text,
                    fontsize=70,
                    color='white',
                    bg_color='black',
                    size=main_video.size,
                    method='caption'
                ).set_duration(3)
                clips.append(intro)
            
            # Add main video
            clips.append(main_video)
            
            # Add outro
            if outro_text:
                outro = TextClip(
                    outro_text,
                    fontsize=70,
                    color='white',
                    bg_color='black',
                    size=main_video.size,
                    method='caption'
                ).set_duration(3)
                clips.append(outro)
            
            # Concatenate
            final = concatenate_videoclips(clips, method="compose")
            
            # Write output
            final.write_videofile(
                output_path,
                codec=VIDEO_CODEC,
                audio_codec='aac',
                fps=self.fps,
                verbose=False,
                logger=None
            )
            
            main_video.close()
            final.close()
            
            return output_path
            
        except ImportError:
            print("[COMPOSER] TextClip not available, skipping intro/outro")
            return video_path
        except Exception as e:
            print(f"[COMPOSER] Error adding intro/outro: {e}")
            return video_path
    
    def apply_effects(self, video_path, effects=None, output_path=None):
        """
        Apply video effects.
        
        Args:
            video_path (str): Path to input video
            effects (list, optional): List of effect names
            output_path (str, optional): Output video path
        
        Returns:
            str: Path to video with effects
        """
        if effects is None or len(effects) == 0:
            return video_path
        
        if output_path is None:
            output_path = os.path.join(TEMP_DIR, f"with_effects_{os.getpid()}.mp4")
        
        try:
            video = VideoFileClip(video_path)
            
            # Apply effects
            for effect in effects:
                if effect == "fadeout":
                    video = video.fx(vfx.fadeout, 1)
                elif effect == "fadein":
                    video = video.fx(vfx.fadein, 1)
                elif effect == "mirror_x":
                    video = video.fx(vfx.mirror_x)
                elif effect == "mirror_y":
                    video = video.fx(vfx.mirror_y)
            
            # Write output
            video.write_videofile(
                output_path,
                codec=VIDEO_CODEC,
                audio_codec='aac',
                fps=self.fps,
                verbose=False,
                logger=None
            )
            
            video.close()
            
            return output_path
            
        except Exception as e:
            print(f"[COMPOSER] Error applying effects: {e}")
            return video_path


def compose_final_video(talking_head_path, background_paths, output_path=None, **kwargs):
    """
    Convenience function to compose final video.
    
    Args:
        talking_head_path (str): Path to talking head video
        background_paths (list or str): Background image path(s)
        output_path (str, optional): Output path
        **kwargs: Additional parameters
    
    Returns:
        str: Path to final video
    """
    composer = VideoComposer()
    return composer.compose_video(talking_head_path, background_paths, output_path, **kwargs)


if __name__ == "__main__":
    print("Video composer module loaded successfully")
