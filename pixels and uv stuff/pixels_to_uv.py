import json

from PIL import Image, ImageColor


def get_pixel_coords(filepath):
    img = Image.open(filepath)
    pixels = img.load()
    width, height = img.size
    mode = img.mode
    coords_dict = {}
    for x in range(width):
        for y in range(height):
            # get rgb value by coords
            r, g, b = pixels[x, y]
            coords_dict[(x, y)] = [r, g, b]
            # in case your image has an alpha channel
            # r, g, b, a = pixels[x, y]
            # print(x, y, f"#{r:02x}{g:02x}{b:02x}")
    return coords_dict, width, height, mode, pixels


def convert_pixel_coords_to_uv(coords: dict, width, height):
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

def convert_pixel_coords_to_uv_list(coords: list, width, height):
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


def DFS(coords: dict, starting_coords, max_width, max_height):
    x, y = starting_coords
    pixel_rgb = coords[(x, y)]
    # IMPORTANT why the fuck is it reading in the blue value one color off from intellij's thing
    # color = ImageColor.getcolor("#dc9cbd", "RGB")
    color = (220, 156, 190)
    acceptable_colors = {color: True}
    queue = []
    visited = {}
    # will store the coords of the ones revealed, only used for online
    # not sure how to do this gracefully...
    revealed = []
    # add it to the queue and the visited
    queue.append(starting_coords)
    # idk what value to store it's arbitrary
    visited[starting_coords] = pixel_rgb
    revealed.append(starting_coords)
    while queue:
        # queue is just a tuple list of coords
        current_coords = queue.pop(0)
        x, y = current_coords
        pixel_rgb = coords[(x, y)]
        # print(queue)
        # print(pixel_rgb)
        # print(color)
        # bottom left row+1, col - 1
        if not (x + 1 >= max_width) and not (y - 1 < 0):
            DFS_helper((x + 1, y - 1), pixel_rgb, acceptable_colors, queue, visited, revealed)
        # left col - 1
        if not (y - 1 < 0):
            DFS_helper((x, y - 1), pixel_rgb, acceptable_colors, queue, visited, revealed)

        # top left row-1, col-1
        if not (x - 1 < 0) and not (y - 1 < 0):
            DFS_helper((x - 1, y - 1), pixel_rgb, acceptable_colors, queue, visited, revealed)

        # top
        if not (x - 1 < 0):
            DFS_helper((x - 1, y), pixel_rgb, acceptable_colors, queue, visited, revealed)

        # top right row-1, col +1
        if not (x - 1 < 0) and not (y + 1 >= max_height):
            DFS_helper((x - 1, y + 1), pixel_rgb, acceptable_colors, queue, visited, revealed)

        # right row, col +1
        if not (y + 1 >= max_height):
            DFS_helper((x, y + 1), pixel_rgb, acceptable_colors, queue, visited, revealed)

        # bottom right row+1, col+1
        if not (x + 1 >= max_width) and not (y + 1 >= max_height):
            DFS_helper((x + 1, y + 1), pixel_rgb, acceptable_colors, queue, visited, revealed)

        # bottom row+1, col
        if not (x + 1 >= max_width):
            DFS_helper((x + 1, y), pixel_rgb, acceptable_colors, queue, visited, revealed)
    # return revealed which should be all matching pixels within range
    print("visited vs revealed")
    print(len(visited.values()))
    print(len(revealed))
    return revealed


def DFS_helper(current_coords, rgb, acceptable_colors: dict, queue, visited: dict, revealed):
    if current_coords not in visited:
        visited[current_coords] = rgb
        # if rgb value is not equal to the targeted rgb then we ignore it and don't continue searching from there
        if tuple(rgb) not in acceptable_colors:
            return
        # if it's acceptable then add to the queue to continue searching from there as well as you know that it's
        # an acceptable rgb value
        queue.append(current_coords)
        revealed.append(current_coords)
    return


def change_pixels_test(filepath, acceptable_pixels, color='#000000'):
    img = Image.open(filepath)
    pixels = img.load()
    # width, height = img.size
    # mode = img.mode
    for pixel in acceptable_pixels:
        pixels[pixel] = ImageColor.getcolor(color, "RGB")
    img.save('test_out.png')

def save_uvs(uv_list):
    with open('uvs.json', 'w') as fp:
        # uvs_list = list(uv_dict.values())
        # print("uvs_list", len(uvs_list))
        print("length of uvs", len(uv_list))
        json.dump({"uvs": uv_list}, fp)

if __name__ == "__main__":
    file = '../images/diffuse.jpg'
    coords_dict, width, height, mode, pixels = get_pixel_coords(file)
    x, y = 155, 2164
    r, g, b = coords_dict[(x, y)]
    starting_coords = (155, 2164)
    print(x, y, f"#{r:02x}{g:02x}{b:02x}")
    # uv_dict = convert_pixel_coords_to_uv(coords_dict, width, height)
    # print(uv_dict[(x, y)])
    acceptable_pixels = DFS(coords_dict, starting_coords, width, height)
    uv_list = convert_pixel_coords_to_uv_list(acceptable_pixels, width, height)
    print(uv_list[0])
    # print(acceptable_pixels)
    # change pixels just to see what it would look like?
    # change_pixels_test(file, acceptable_pixels)
    # print("Saving...")
    save_uvs(uv_list)