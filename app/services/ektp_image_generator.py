"""
e-KTP Image Generator Module
Generates Indonesian e-KTP (Electronic ID Card) images based on provided JSON data.
Supports photo input as file path, URL, or base64 encoded string.
"""

import os
import json
import base64
import requests
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

class EKTPImageGenerator:
    """Main class for generating e-KTP images from JSON data."""

    def __init__(self):
        """
        Initialize the generator with environment variables.
        """
        self.template_path = self._get_template_path()
        self.font_sizes = [25, 32, 16, 25]  # Font sizes: [province, NIK, data, signature]
        self.setup_fonts()

    def _get_template_path(self):
        """Get template path from environment variables."""
        template_path = os.getenv('TEMPLATE_FILE_PATH')
        if not template_path:
            raise ValueError("TEMPLATE_FILE_PATH not found in .env file")
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template file not found at {template_path}")
        return template_path

    def setup_fonts(self):
        """Initialize all required fonts with proper sizing."""
        try:
            self.fonts = {
                'province': ImageFont.truetype('datasets/fonts/arial.ttf', self.font_sizes[0]),
                'nik': ImageFont.truetype('datasets/fonts/ocrb.ttf', self.font_sizes[1]),
                'data': ImageFont.truetype('datasets/fonts/arial.ttf', self.font_sizes[2]),
                'signature': ImageFont.truetype('datasets/fonts/signature.ttf', self.font_sizes[3])
            }
        except IOError as e:
            raise Exception(f"Font file not found or invalid: {str(e)}")

    def _load_image_from_source(self, photo_source):
        """
        Load image from various sources (path, URL, or base64).

        Args:
            photo_source (str): Path, URL, or base64 encoded image

        Returns:
            Image: PIL Image object
        """
        try:
            # Check if source is base64
            if photo_source.startswith('data:image'):
                header, encoded = photo_source.split(',', 1)
                return Image.open(BytesIO(base64.b64decode(encoded)))

            # Check if source is URL
            if urlparse(photo_source).scheme in ('http', 'https'):
                response = requests.get(photo_source)
                response.raise_for_status()
                return Image.open(BytesIO(response.content))

            # Assume it's a file path
            if os.path.exists(photo_source):
                return Image.open(photo_source)

            raise ValueError("Invalid photo source - must be valid path, URL, or base64")

        except Exception as e:
            raise Exception(f"Could not load image from source: {str(e)}")

    def process_photo(self, template, photo_source):
        """
        Process and paste the passport photo onto the template.
        Supports path, URL, or base64 encoded image.

        Args:
            template (Image): The base template image
            photo_source (str): Path, URL, or base64 encoded image

        Returns:
            Image: Template with photo pasted
        """
        try:
            pas_photo = self._load_image_from_source(photo_source)

            # Maintain original photo processing logic
            # if pas_photo.size[0] != 432:
            #     cropped = pas_photo.crop((0, 0, 432, 450))
            #     resized = cropped.resize((
            #         round(pas_photo.size[0] * 0.4),
            #         round(pas_photo.size[1] * 0.4)
            #     ))
            # else:
            #     resized = pas_photo.resize((
            #         round(pas_photo.size[0] * 0.4),
            #         round(pas_photo.size[1] * 0.4)
            #     ))
            resized = self.object_fit_cover(pas_photo, 185, 230)

            template.paste(resized, (520, 120))
            return template

        except Exception as e:
            raise Exception(f"Could not process photo: {str(e)}")

    def object_fit_cover(self, img, target_width, target_height):
        # Rasio target
        target_ratio = target_width / target_height
        original_width, original_height = img.size
        original_ratio = original_width / original_height

        # Crop berdasarkan rasio
        if original_ratio > target_ratio:
            # Gambar lebih lebar → potong kiri kanan
            new_width = int(original_height * target_ratio)
            offset = (original_width - new_width) // 2
            box = (offset, 0, offset + new_width, original_height)
        else:
            # Gambar lebih tinggi → potong atas bawah
            new_height = int(original_width / target_ratio)
            offset = (original_height - new_height) // 2
            box = (0, offset, original_width, offset + new_height)

        cropped = img.crop(box)
        return cropped.resize((target_width, target_height), Image.Resampling.LANCZOS)

    def generate_signature(self, full_name):
        """
        Generate signature text from full name (first word only).

        Args:
            full_name (str): Complete name string

        Returns:
            str: First name for signature
        """
        return full_name.split()[0]

    def draw_text_elements(self, draw, data):
        """
        Draw all text elements onto the image with precise original positioning.

        Args:
            draw (ImageDraw): Drawing context
            data (dict): All e-KTP data fields
        """
        # Province and City (exact original positions)
        draw.text((380, 45), f"PROVINSI {data['province'].upper()}",
                 fill="black", font=self.fonts['province'], anchor="ms")
        draw.text((380, 70), f"KOTA {data['city'].upper()}",
                 fill="black", font=self.fonts['province'], anchor="ms")

        birth_info = f"{data['place_of_birth'].upper()}, {data['birth_date']}"

        # Personal data (maintain all original coordinates)
        draw.text((170, 105), data["nik"], fill="black", font=self.fonts['nik'], anchor="lt")
        draw.text((190, 145), data["full_name"].upper(), fill="black", font=self.fonts['data'], anchor="lt")
        draw.text((190, 168), birth_info, fill="black", font=self.fonts['data'], anchor="lt")
        draw.text((190, 191), data["gender"].upper(), fill="black", font=self.fonts['data'], anchor="lt")
        draw.text((463, 190), data["blood_type"].upper(), fill="black", font=self.fonts['data'], anchor="lt")
        draw.text((190, 212), data["address"].upper(), fill="black", font=self.fonts['data'], anchor="lt")
        draw.text((190, 234), data["rt_rw"].upper(), fill="black", font=self.fonts['data'], anchor="lt")
        draw.text((190, 257), data["village"].upper(), fill="black", font=self.fonts['data'], anchor="lt")
        draw.text((190, 279), data["district"].upper(), fill="black", font=self.fonts['data'], anchor="lt")
        draw.text((190, 300), data["religion"].upper(), fill="black", font=self.fonts['data'], anchor="lt")
        draw.text((190, 323), data["marital_status"].upper(), fill="black", font=self.fonts['data'], anchor="lt")
        draw.text((190, 346), data["occupation"].upper(), fill="black", font=self.fonts['data'], anchor="lt")
        draw.text((190, 369), data["citizenship"].upper(), fill="black", font=self.fonts['data'], anchor="lt")
        draw.text((190, 390), data["expiry_date"].upper(), fill="black", font=self.fonts['data'], anchor="lt")

        # Footer elements
        small_font = ImageFont.truetype('datasets/fonts/arial.ttf', 12)

        draw.text((520, 360), f"{data['city'].upper()}", fill="black", font=small_font, anchor="lt")
        draw.text((520, 380), data["issue_date"], fill="black", font=small_font, anchor="lt")

        # Signature (first name only)
        signature = self.generate_signature(data["full_name"])
        draw.text((530, 405), signature, fill="black", font=self.fonts['signature'], anchor="lt")

    def generate(self, input_data, output_dir="outputs/results"):
        """
        Main generation method that produces the e-KTP image.

        Args:
            input_data (dict): All required e-KTP data fields with 'photo' as path, URL, or base64
            output_dir (str): Directory to save output images

        Returns:
            dict: {
                "image_path": str,
                "base64_image": str
            }
        """
        try:
            # Ensure output directory exists
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            # Load template from environment variable
            template = Image.open(self.template_path)

            # Process photo (now accepts path, URL, or base64)
            template = self.process_photo(template, input_data["photo_path"])

            # Prepare drawing context
            draw = ImageDraw.Draw(template)

            # Draw all text elements
            self.draw_text_elements(draw, input_data)

            # Save result
            output_filename = f"ektp_{input_data['nik']}.jpg"
            output_path = os.path.join(output_dir, output_filename)
            template.save(output_path, quality=95)

            # Generate base64
            with open(output_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            return {
                "image_path": output_path,
                "base64_image": base64_image
            }

        except Exception as e:
            raise Exception(f"Error during e-KTP image generation: {str(e)}")