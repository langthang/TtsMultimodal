import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from lxml import etree
from pptx.util import Inches
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Cm
from pptx.enum.shapes import MSO_SHAPE
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
        title_shape.fill.solid()
        title_shape.fill.fore_color.rgb = RGBColor(*self.config.slide_text_background_color)  # Background color
        self._set_shape_transparency(title_shape, 75000)
        for paragraph in title_shape.text_frame.paragraphs:
            for run in paragraph.runs:
                run.font.name = self.config.slide_title_font_name
                run.font.color.rgb = RGBColor(*self.config.slide_title_font_color)
                run.font.size = Pt(self.config.slide_title_font_size)
                # Set text background color and opacity
                run.font.highlight_color = RGBColor(*self.config.slide_text_background_color)  # Apply background color (highlight effect)
                run.font.transparency = 0.25  # 75% opacity (transparency in PowerPoint works inversely)


    def _add_content(self, slide, content: str):
        """Add content to slide."""
        content_shape = slide.placeholders[1]
        content_shape.text_frame.clear()

        content_shape.fill.solid()
        content_shape.fill.fore_color.rgb = RGBColor(*self.config.slide_text_background_color)  # Background color
        self._set_shape_transparency(content_shape, 75000) # (100-t)*1000 where t is the level of transparency you want in %

        # Process content to ensure left-aligned line-by-line formatting
        content_lines = [line.strip() for line in content.split("\n") if line.strip()]

        for line in content_lines:
            p = content_shape.text_frame.add_paragraph()
            p.text = line
            p.font.name = self.config.slide_content_font_name
            p.font.color.rgb = RGBColor(*self.config.slide_content_font_color)
            p.font.size = Pt(self.config.slide_content_font_size)

            # Remove bullet points and align text properly
            p._pPr.insert(0, etree.Element("{http://schemas.openxmlformats.org/drawingml/2006/main}buNone"))
            p.alignment = PP_ALIGN.LEFT


    def SubElement(self, parent, tagname, **kwargs):
        element = OxmlElement(tagname)
        element.attrib.update(kwargs)
        parent.append(element)
        return element
    
    def _set_shape_transparency(self, shape, alpha):
        """ Set the transparency (alpha) of a shape"""
        ts = shape.fill._xPr.solidFill
        sF = ts.get_or_change_to_srgbClr()
        sE = self.SubElement(sF, 'a:alpha', val=str(alpha))


    # def _add_content(self, slide, content: str):
    #     """Add content to slide with an opaque text box per line."""
    #     content_shape = slide.placeholders[1]
    #     content_shape.text_frame.clear()

    #     content_lines = [line.strip() for line in content.split("\n") if line.strip()]
        
    #     top_position = Inches(2)  # Adjust the starting position for text boxes
        
    #     for line in content_lines:
    #         # Create a textbox
    #         text_box = slide.shapes.add_textbox(Inches(1), top_position, Inches(6), Inches(0.2))
    #         text_frame = text_box.text_frame
    #         text_frame.clear()

    #         p = text_frame.add_paragraph()
    #         p.text = line
    #         p.font.name = self.config.slide_content_font_name
    #         p.font.color.rgb = RGBColor(*self.config.slide_content_font_color)
    #         p.font.size = Pt(self.config.slide_content_font_size)
    #         p.alignment = PP_ALIGN.LEFT

    #         # Set opaque background for the text box
    #         text_box.fill.solid()
    #         text_box.fill.fore_color.rgb = RGBColor(219, 141, 208)  # Background color

    #         content_shape.fill.solid()
    #         content_shape.fill.fore_color.rgb = RGBColor(219, 141, 208)  # Background color
    #         #text_box.fill.transparency = 0.25  # 75% opacity

    #         self._set_shape_transparency(text_box, 20000)
    #         self._set_shape_transparency(content_shape, 60000)

    #         # Increment position for next text box
    #         top_position += Inches(1)

