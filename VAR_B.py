import geopandas as gpd
import numpy as np
from PIL import Image, ImageDraw
from shapely.geometry import Polygon, MultiPolygon
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def generate_ishihara_map(
    image_size=1024,
    circle_radius=480,
    dot_radius=3,
    dot_spacing=8,
    map_dot_color=(220, 50, 50),
    background_color_range=(80, 220),
    output_path="ishihara_map_output",
    export_format="PNG"  # options: PNG, PDF, SVG
):
    # Create background image
    img = Image.new("RGB", (image_size, image_size), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    np.random.seed(42)
    for x in range(0, image_size, dot_spacing):
        for y in range(0, image_size, dot_spacing):
            dx, dy = x - image_size // 2, y - image_size // 2
            if dx**2 + dy**2 <= circle_radius**2:
                color = tuple(np.random.randint(*background_color_range, size=3))
                draw.ellipse((x - dot_radius, y - dot_radius, x + dot_radius, y + dot_radius), fill=color)

    # Load Georgia geometry
    world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
    georgia = world[world["name"] == "Georgia"].to_crs(epsg=3857)
    geometry = georgia.geometry.values[0]

    bounds = geometry.bounds
    scale_x = (circle_radius * 1.6) / (bounds[2] - bounds[0])
    scale_y = (circle_radius * 1.6) / (bounds[3] - bounds[1])
    scale = min(scale_x, scale_y)

    def transform_coords(coords):
        return [
            (
                int((x - (bounds[0] + bounds[2]) / 2) * scale + image_size // 2),
                int((y - (bounds[1] + bounds[3]) / 2) * -scale + image_size // 2)
            )
            for x, y in coords
        ]

    def draw_geometry(geom):
        if isinstance(geom, Polygon):
            rings = [geom.exterior] + list(geom.interiors)
        elif isinstance(geom, MultiPolygon):
            for part in geom.geoms:
                draw_geometry(part)
            return
        else:
            return

        for ring in rings:
            coords = transform_coords(ring.coords)
            for x, y in coords:
                for dx in range(-dot_radius, dot_radius + 1):
                    for dy in range(-dot_radius, dot_radius + 1):
                        if dx**2 + dy**2 <= dot_radius**2:
                            px, py = x + dx, y + dy
                            if 0 <= px < image_size and 0 <= py < image_size:
                                img.putpixel((px, py), map_dot_color)

    draw_geometry(geometry)

    # Save output
    if export_format.upper() == "PNG":
        final_path = output_path + ".png"
        img.save(final_path)
    elif export_format.upper() == "PDF":
        final_path = output_path + ".pdf"
        with PdfPages(final_path) as pdf:
            fig = plt.figure(figsize=(image_size / 100, image_size / 100), dpi=100)
            plt.imshow(img)
            plt.axis("off")
            pdf.savefig(fig, bbox_inches='tight', pad_inches=0)
            plt.close()
    elif export_format.upper() == "SVG":
        # Convert to matplotlib for SVG
        fig = plt.figure(figsize=(image_size / 100, image_size / 100), dpi=100)
        plt.imshow(img)
        plt.axis("off")
        final_path = output_path + ".svg"
        plt.savefig(final_path, format='svg', bbox_inches='tight', pad_inches=0)
        plt.close()
    else:
        raise ValueError("Unsupported format. Use PNG, PDF or SVG.")

    print(f"✅ ფაილი შენახულია: {final_path}")

# მაგალითის გაშვება
generate_ishihara_map(
    image_size=1024,
    circle_radius=460,
    dot_radius=3,
    dot_spacing=8,
    map_dot_color=(200, 0, 0),
    output_path="ishihara_georgia_B",
    export_format="PNG"
)
