import time
import numpy as np
import cv2
from PIL import Image, ImageColor

texture_file_path = 'obj textures/diffuse.jpg'


def open_Image_Pillow():
    start = time.perf_counter()

    print("Grabbing pixels and rgbs....")
    img = Image.open(texture_file_path)
    data = img.load()
    print(data[0,0])
    end = time.perf_counter()
    print(f"pillow Time {end - start}")


def open_Image_Pillow_numpy():
    start = time.perf_counter()
    print("Numpy image....")
    img = Image.open(texture_file_path)
    data = np.array(img)
    end = time.perf_counter()
    print(f"NUMPY pillow Time {end - start}")
    y, x = 1000, 550
    # numpy is flipped!
    print(data[0][0])
    print(data.dtype)
    print(data.shape)



# def open_image_CV2():
#     start = time.perf_counter()
#     print("CV2")
#     img = cv2.imread(texture_file_path)
#     rows, cols, _ = img.shape
#     end = time.perf_counter()
#     print(f"CV2 Time {end - start}")

# def get_pixel_coords(self):
#         img = Image.open(self.texture_file)
#         pixels = img.load()
#         width, height = img.size
#         mode = img.mode
#         coords_dict = {}
#         for x in range(width):
#             for y in range(height):
#                 r, g, b = pixels[x, y]
#                 coords_dict[(x, y)] = [r, g, b]
#         img.close()
#         return coords_dict, width, height, mode, pixels
# path

open_Image_Pillow()
# open_image_CV2()
open_Image_Pillow_numpy()

