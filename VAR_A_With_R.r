# საჭიროა პაკეტები
library(sf)
library(ggplot2)
library(dplyr)
library(ggforce)

# პარამეტრები
image_size <- 1024
circle_radius <- 480
dot_radius <- 3
dot_spacing <- 8

# წერტილების გენერაცია
dot_grid <- expand.grid(
  x = seq(0, image_size, by = dot_spacing),
  y = seq(0, image_size, by = dot_spacing)
) %>%
  mutate(
    dx = x - image_size / 2,
    dy = y - image_size / 2,
    dist = sqrt(dx^2 + dy^2)
  ) %>%
  filter(dist <= circle_radius) %>%
  rowwise() %>%
  mutate(
    r = sample(80:220, 1),
    g = sample(80:220, 1),
    b = sample(80:220, 1),
    color = rgb(r, g, b, maxColorValue = 255)
  )

# რუკის ჩატვირთვა
abasha <- st_read("ishihara/shp/abasha_line.shp", quiet = TRUE)

# ცენტრირება და მასშტაბირება
bounds <- st_bbox(abasha)
scale_x <- (circle_radius * 1.6) / (bounds["xmax"] - bounds["xmin"])
scale_y <- (circle_radius * 1.6) / (bounds["ymax"] - bounds["ymin"])
scale <- min(scale_x, scale_y)

# ცენტრირებული გეომეტრია
abasha_centered <- abasha %>%
  st_transform(4326) %>%
  st_geometry() %>%
  st_translate(-mean(c(bounds["xmin"], bounds["xmax"])),
               -mean(c(bounds["ymin"], bounds["ymax"]))) %>%
  `*`(scale) %>%
  st_translate(image_size / 2, image_size / 2)

# ფონის წერტილების და რუკის დახატვა
p <- ggplot() +
  geom_point(data = dot_grid, aes(x = x, y = y), color = dot_grid$color, size = 0.9) +
  geom_sf(data = abasha_centered, color = "red", size = 0.4) +
  theme_void() +
  coord_fixed(xlim = c(0, image_size), ylim = c(0, image_size), expand = FALSE)

# შენახვა
ggsave("ishihara/ishihara_abasha_A_variant_R.png", plot = p, width = 1024/100, height = 1024/100, dpi = 100)
