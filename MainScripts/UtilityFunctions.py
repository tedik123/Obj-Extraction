# ignore this because it returns a dictionary which we don't want
import math


def convert_pixel_coords_to_uv( coords: dict, width, height):
    # u is width, v is height
    # coords tuple will be key
    uv_dict = {}
    for coord, rgb in coords.items():
        x, y = coord
        r, g, b = rgb
        u = x / width
        # since 0, 0 is at the bottom left! very important
        v = 1 - y / height
        uv_dict[coord] = (u, v)
    return uv_dict
# we actually don't need to use this because in the end we only use pixels not uvs!
# also the way it is now needs to be changed as it won't work with the updated version
def convert_pixel_coords_to_uv_list( coords: list, width, height):
        # u is width, v is height
        uvs_list = []
        for coord in coords:
            x, y = coord
            # r, g, b = rgb
            u = x / width
            # since 0, 0 is at the bottom left! very important
            v = 1 - y / height
            uvs_list.append([u, v])
        return uvs_list


def uvs_to_pixels(u, v):
    MAX_WIDTH = 4096
    MAX_HEIGHT = 4096
    # since pixels are only ints we need to floor or use ceiling
    x = math.floor(u * MAX_WIDTH)
    # since 0, 0 is at the bottom left! very important
    y = math.floor((v - 1) * -MAX_HEIGHT)
    return x, y