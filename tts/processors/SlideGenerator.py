import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from lxml import etree
from AppConfig import AppConfig

class SlideGenerator:
    def __init__(self):
        self.slide_width = Inches(13.33)
        self.slide_height = Inches(7.5)
        self.config = AppConfig()

    def create_slide(self, title: str, content: str, background_image: str, output_file: str) -> str:
        """Create a slide with the given content and return the file path."""
        presentation = Presentation()
        presentation.slide_width = self.slide_width
        presentation.slide_height = self.slide_height

        slide = presentation.slides.add_slide(presentation.slide_layouts[1])
        
        # Add background if exists
        if background_image and os.path.exists(background_image):
            self._add_background(slide, background_image)

        # Add content
        if title:
            self._add_title(slide, title)
        if content:
            self._add_content(slide, content)

        # Save presentation
        presentation.save(output_file)
        return output_file

    def _add_background(self, slide, background_image: str):
        """Add background image to slide."""
        background_shape = slide.shapes.add_picture(
            background_image, 0, 0, 
            width=self.slide_width, 
            height=self.slide_height
        )
        slide.shapes._spTree.remove(background_shape._element)
        slide.shapes._spTree.insert(2, background_shape._element)

    def _add_title(self, slide, title: str):
        """Add title to slide."""
        title_shape = slide.shapes.title
        title_shape.text = title
        for paragraph in title_shape.text_frame.paragraphs:
            for run in paragraph.runs:
                run.font.name = self.config.slide_title_font_name
                run.font.color.rgb = RGBColor(*self.config.slide_title_font_color)
                run.font.size = Pt(self.config.slide_title_font_size)

    def _add_content(self, slide, content: str):
        """Add content to slide."""
        content_shape = slide.placeholders[1]
        content_shape.text_frame.clear()
        p = content_shape.text_frame.add_paragraph()
        p.text = content
        p.font.name = self.config.slide_content_font_name
        p.font.color.rgb = RGBColor(*self.config.slide_content_font_color)
        p.font.size = Pt(self.config.slide_content_font_size)
        p._pPr.insert(0, etree.Element("{http://schemas.openxmlformats.org/drawingml/2006/main}buNone"))
        p.alignment = PP_ALIGN.CENTER
