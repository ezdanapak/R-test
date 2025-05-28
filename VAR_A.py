import geopandas as gpd
import numpy as np
from PIL import Image, ImageDraw
from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString

# პარამეტრები
image_size = 1024
circle_radius = 480
dot_radius = 3
dot_spacing = 8

# ფონის წერტილების გენერაცია
img = Image.new("RGB", (image_size, image_size), (255, 255, 255))
draw = ImageDraw.Draw(img)

np.random.seed(42)
for x in range(0, image_size, dot_spacing):
    for y in range(0, image_size, dot_spacing):
        dx = x - image_size // 2
        dy = y - image_size // 2
        if dx ** 2 + dy ** 2 <= circle_radius ** 2:
            color = tuple(np.random.randint(80, 220, size=3))  # ფერადი წერტილები
            draw.ellipse((x - dot_radius, y - dot_radius, x + dot_radius, y + dot_radius), fill=color)

# Shapefile-ის ჩატვირთვა და CRS-ის მინიჭება
line_gdf = gpd.read_file("ishihara/shp/abasha_line.shp")
line_gdf.set_crs(epsg=4326, inplace=True)     # საჭიროების მიხედვით შეცვალე EPSG
line_gdf = line_gdf.to_crs(epsg=3857)         # ვიზუალური მასშტაბისთვის ვ_PROJECT-ავთ

geometry = line_gdf.unary_union  # ერთობლივი გეომეტრია

# მასშტაბის გამოთვლა და ცენტრირება
bounds = geometry.bounds
scale_x = (circle_radius * 1.6) / (bounds[2] - bounds[0])
scale_y = (circle_radius * 1.6) / (bounds[3] - bounds[1])
scale = min(scale_x, scale_y)

def transform_coords(coords):
    transformed = []
    for x, y in coords:
        tx = (x - (bounds[0] + bounds[2]) / 2) * scale + image_size // 2
        ty = (y - (bounds[1] + bounds[3]) / 2) * -scale + image_size // 2
        transformed.append((int(tx), int(ty)))
    return transformed

# ხაზოვანი გეომეტრიის დახატვა
def draw_line_geometry(geom):
    if isinstance(geom, (LineString, Polygon)):
        coords = transform_coords(geom.exterior.coords if isinstance(geom, Polygon) else geom.coords)
        for x, y in coords:
            for dx in range(-dot_radius, dot_radius + 1):
                for dy in range(-dot_radius, dot_radius + 1):
                    if dx**2 + dy**2 <= dot_radius**2:
                        px, py = x + dx, y + dy
                        if 0 <= px < image_size and 0 <= py < image_size:
                            img.putpixel((px, py), (220, 50, 50))  # წითლად ხაზების გამოსახვა
    elif isinstance(geom, (MultiLineString, MultiPolygon)):
        for part in geom.geoms:
            draw_line_geometry(part)

# დახატვა
draw_line_geometry(geometry)

# შენახვა
img.save("ishihara/ishihara_abasha_A_variant.png")

print("შენახულია: ishihara_abasha_A_variant.png")
