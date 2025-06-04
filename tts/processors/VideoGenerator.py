import os
import subprocess
from pdf2image import convert_from_path
from moviepy import *
from AppConfig import AppConfig

class VideoGenerator:
    def __init__(self):
        self.config = AppConfig()

    def create_video(self, slide_file: str, audio_file: str, audio_length: int, output_file: str) -> str:
        """Create a video from slide and audio."""
        slide_image_file = self._convert_slide_to_image(slide_file)
        if not slide_image_file:
            return None

        # Create video clip
        image_clip = ImageClip(
            img=slide_image_file, 
            duration=(audio_length / 1000) + 1
        ).resized((1920, 1080))
        
        # Generate video with audio
        image_clip.write_videofile(
            output_file,
            fps=self.config.video_fps,
            codec=f"{self.config.image_to_video_codec}",
            audio=audio_file,
            audio_codec=f"{self.config.text_to_audio_codec}"
        )

        return output_file

    def _convert_slide_to_image(self, slide_file: str) -> str:
        """Convert slide to image using either PDF or direct PNG conversion."""
        slide_image_dir = os.path.abspath(os.path.dirname(slide_file))
        base_name = os.path.splitext(os.path.basename(slide_file))[0]

        if self.config.slide_generation_mode_pdf:
            return self._convert_via_pdf(slide_file, slide_image_dir, base_name)
        else:
            return self._convert_to_png(slide_file, slide_image_dir, base_name)

    def _convert_via_pdf(self, slide_file: str, output_dir: str, base_name: str) -> str:
        """Convert slide to image via PDF intermediate step."""
        try:
            # Convert to PDF
            subprocess.run([
                "soffice",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                output_dir,
                slide_file,
            ], check=True)

            pdf_file = os.path.join(output_dir, f"{base_name}.pdf")
            if not os.path.exists(pdf_file):
                return None

            # Convert PDF to PNG
            png_file = os.path.join(output_dir, f"{base_name}.png")
            images = convert_from_path(pdf_file, dpi=900)
            images[0].save(png_file, 'PNG')
            return png_file

        except subprocess.CalledProcessError as e:
            print(f"Error converting slide to PDF: {e}")
            return None

    def _convert_to_png(self, slide_file: str, output_dir: str, base_name: str) -> str:
        """Convert slide directly to PNG."""
        try:
            subprocess.run([
                "soffice",
                "--headless",
                "--convert-to",
                "png",
                "--outdir",
                output_dir,
                slide_file,
            ], check=True)

            png_file = os.path.join(output_dir, f"{base_name}.png")
            return png_file if os.path.exists(png_file) else None

        except subprocess.CalledProcessError as e:
            print(f"Error converting slide to PNG: {e}")
            return None
