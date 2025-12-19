from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import piexif
import svgwrite
import xml.etree.ElementTree as ET
from pathlib import Path

class ImgTek:
    # --- Raster Image Processing ---
    def load(self, path):
        img = Image.open(path)
        img.load()
        return img

    def save(self, img, path, format=None):
        img.save(path, format=format)

    def resize(self, img, width, height):
        return img.resize((width, height), Image.LANCZOS)

    def rotate(self, img, degrees):
        return img.rotate(degrees, expand=True)

    def convert_format(self, img, target_format):
        if target_format.upper() == "JPEG" and img.mode in ("RGBA", "LA"):
            img = img.convert("RGB")
        return img

    def get_pixel(self, img, x, y):
        return img.getpixel((x, y))

    def set_pixel(self, img, x, y, value):
        img.putpixel((x, y), value)

    # --- Metadata Handling ---
    def get_metadata(self, path):
        return piexif.load(str(path))

    def set_metadata(self, img, metadata_dict, output_path, output_format='JPEG'):
        exif_bytes = piexif.dump(metadata_dict)
        img.save(output_path, format=output_format, exif=exif_bytes)

    # --- Vector Drawing on Raster Images ---
    def draw_line(self, img, start, end, color=(255, 0, 0), width=1):
        draw = ImageDraw.Draw(img)
        draw.line([start, end], fill=color, width=width)
        return img

    def draw_rectangle(self, img, top_left, bottom_right, outline=(0, 255, 0), width=1, fill=None):
        draw = ImageDraw.Draw(img)
        draw.rectangle([top_left, bottom_right], outline=outline, width=width, fill=fill)
        return img

    def draw_circle(self, img, center, radius, outline=(0, 0, 255), width=1, fill=None):
        draw = ImageDraw.Draw(img)
        bbox = [(center[0]-radius, center[1]-radius), (center[0]+radius, center[1]+radius)]
        draw.ellipse(bbox, outline=outline, width=width, fill=fill)
        return img

    def draw_polygon(self, img, points, outline=(255, 255, 0), width=1, fill=None):
        draw = ImageDraw.Draw(img)
        draw.polygon(points, outline=outline, fill=fill)
        if width > 1:
            for i in range(len(points)):
                draw.line([points[i], points[(i+1) % len(points)]], fill=outline, width=width)
        return img

    # --- Filters ---
    def apply_blur(self, img, radius=2):
        return img.filter(ImageFilter.GaussianBlur(radius))

    def apply_sharpen(self, img):
        return img.filter(ImageFilter.SHARPEN)

    def apply_edge_enhance(self, img):
        return img.filter(ImageFilter.EDGE_ENHANCE)

    def apply_grayscale(self, img):
        return img.convert("L")

    def apply_sepia(self, img):
        sepia_img = img.convert("RGB")
        width, height = sepia_img.size
        pixels = sepia_img.load()

        for py in range(height):
            for px in range(width):
                r, g, b = pixels[px, py]

                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)

                pixels[px, py] = (
                    min(tr, 255),
                    min(tg, 255),
                    min(tb, 255),
                )
        return sepia_img

    def apply_contrast(self, img, factor=1.5):
        enhancer = ImageEnhance.Contrast(img)
        return enhancer.enhance(factor)

    def apply_brightness(self, img, factor=1.5):
        enhancer = ImageEnhance.Brightness(img)
        return enhancer.enhance(factor)

    # --- SVG Vector Support ---
    def create_svg(self, filename, width, height):
        dwg = svgwrite.Drawing(str(filename), size=(width, height))
        return dwg

    def svg_add_line(self, dwg, start, end, stroke='red', stroke_width=1):
        dwg.add(dwg.line(start=start, end=end, stroke=stroke, stroke_width=stroke_width))

    def svg_add_rectangle(self, dwg, insert, size, stroke='green', stroke_width=1, fill='none'):
        dwg.add(dwg.rect(insert=insert, size=size, stroke=stroke, stroke_width=stroke_width, fill=fill))

    def svg_add_circle(self, dwg, center, r, stroke='blue', stroke_width=1, fill='none'):
        dwg.add(dwg.circle(center=center, r=r, stroke=stroke, stroke_width=stroke_width, fill=fill))

    def svg_add_polygon(self, dwg, points, stroke='yellow', stroke_width=1, fill='none'):
        dwg.add(dwg.polygon(points=points, stroke=stroke, stroke_width=stroke_width, fill=fill))

    def svg_save(self, dwg):
        dwg.save()

    def parse_svg(self, filepath):
        tree = ET.parse(filepath)
        root = tree.getroot()
        ns = {'svg': 'http://www.w3.org/2000/svg'}

        elements = {
            "paths": root.findall('.//svg:path', ns),
            "circles": root.findall('.//svg:circle', ns),
            "rects": root.findall('.//svg:rect', ns),
            "polygons": root.findall('.//svg:polygon', ns),
            "lines": root.findall('.//svg:line', ns),
        }
        return elements

if __name__ == "__main__":
    # Example usage
    imgtek = ImgTek()

    img_path = Path("input.jpg")
    svg_path = Path("example.svg")
    output_img_path = Path("output.png")

    img = imgtek.load(img_path)
    img = imgtek.resize(img, 800, 600)
    img = imgtek.draw_line(img, (10, 10), (300, 300), color=(255, 0, 0), width=5)
    img = imgtek.apply_sepia(img)
    imgtek.save(img, output_img_path)

    elements = imgtek.parse_svg(svg_path)
    print("SVG elements found:", {k: len(v) for k, v in elements.items()})