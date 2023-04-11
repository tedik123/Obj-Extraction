import json
import time
from concurrent.futures import ProcessPoolExecutor
from os import listdir
from os.path import isfile, join
from PixelToFace import PixelToFace
from PixelGrabber import PixelGrabber
from PixelIndexer import PixelIndexer
from PixelGrabber import save_pixels_by_labels
from ObjFileToGeometryFiles import ObjToGeometryFiles
from PixelToFace import get_image_dimensions

def create_file_names_list():
    ignore_files = [".gitkeep", "human.obj", "file_list.json"]
    mypath = "outputs/OBJ files/"
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f not in ignore_files]
    # add our actual big human anatomy object to the list as well
    # onlyfiles.append("Anatomy.OBJ")
    for i, file in enumerate(onlyfiles):
        onlyfiles[i] = file.removesuffix(".obj")
    json_object = {"label_names": onlyfiles}
    with open("outputs/OBJ files/label_list.json", "w") as fh:
        json.dump(json_object, fh)
    print("Creating file/label list.")




if __name__ == "__main__":
    # IMPORTANT  this is an array of strings, if it's empty it will do all of them

    label_names_to_test = []

    # texture_file_path = 'obj textures/diffuse.jpg'
    texture_file_path = 'obj textures/girl_texture.jpg'

    # if there's a fade or variation in color you will want to raise this to loosen what is an acceptable color
    default_pixel_deviation = 3

    # set white as the default acceptable colors
    default_acceptable_colors = [[255, 255, 255]]
    deviation_default_colors = 2

    # base_obj_file_path = "obj files/anatomy.OBJ"
    base_obj_file_path = "obj files/girl_100k.obj"

    # choose whether to save the uvs and normals, if both are false it will only save the vertices and faces
    SAVE_UVS = True
    SAVE_NORMALS = True

    # by default will use max threads available - 1
    THREAD_COUNT = None

    # if you only want to run certain scripts you can change accordingly here
    RUN_PIXEL_GRABBER = True
    RUN_PIXEL_TO_FACE = False
    RUN_PIXEL_INDEXER = False

    # this triangle decomposer only needs to be run once if the base .obj file is the same! So turn it to false, after!
    RUN_TRIANGLE_DECOMPOSER = False

    # IMPORTANT unless you're testing something you can just leave it
    # target is what pixels we're trying to find
    TARGET_FILE = 'outputs/pixels_by_labels.bin'

    # these will be created later
    texture_max_width, texture_max_height = None, None

    start0 = time.time()
    if RUN_PIXEL_GRABBER:
        # first create the object which simply loads in the diffuse.jpg and relevant data
        # also reads in the label starts
        pixel_grabber = PixelGrabber(texture_file_path, label_names_to_test, default_pixel_deviation)

        # allows for a default color range to capture more of the label (if you have it), disable it if too aggressive
        # pixel_grabber.disable_default_color_range()

        # this is for the future processes
        executor = ProcessPoolExecutor(max_workers=1)

        # although this takes forever it is not worth optimizing as it is a task that must be waited on
        # before anything else is run
        pixel_grabber.read_in_image_data()
        texture_max_width, texture_max_height = pixel_grabber.get_image_dimensions()

        # creates the range of acceptable colors by label, in this case just white basically
        pixel_grabber.create_acceptable_colors_by_label(default_acceptable_colors, deviation_default_colors)

        # then run the actual pixel_grabber algo
        pixel_grabber.run_pixel_grabber(THREAD_COUNT)

        #  to save the pixels by label
        # you can specify an output file name as an argument if you want (optional)
        output_file_name = "pixels_by_labels"
        futures = [executor.submit(save_pixels_by_labels, pixel_grabber.pixels_by_label, output_file_name)]

        # pixel_grabber.save_pixels_by_labels() # run for better print statements without process pool

        # if you are testing, you can visualize the changes with the change_pixels_test
        # you can specify a specific hex color default is '#000000'
        hex_color = '#000000'
        pixel_grabber.run_change_pixels_test(hex_color)

        executor.shutdown(wait=True, cancel_futures=False)
        print("Finished saving pixel change test file and pixel by label file")

        end = time.time()
        print()
        print(f"Finished finding pixels...Took {end - start0} seconds")

    ###################################################################################################################
    ### NEW SCRIPT STARTS HERE ###
    if RUN_PIXEL_TO_FACE:
        print("Starting pixels to faces code!")

        if RUN_TRIANGLE_DECOMPOSER:
            start = time.time()
            # we need this to create the geometry files and again only needs
            # to be run once, so it's paired with the triangle decomposer
            obj_to_json = ObjToGeometryFiles(base_obj_file_path)
            obj_to_json.read_in_OBJ_file()
            obj_to_json.insert_face_data()
            obj_to_json.create_json_files()
            end = time.time()
            print()
            print(f"Finished creating geometries...Took {end - start} seconds")

        preload_STRtree = not RUN_TRIANGLE_DECOMPOSER
        start = time.time()

        # need to grab the texture dimensions
        if texture_max_width is None:
            print("Grabbing texture images")
            texture_max_width, texture_max_height = get_image_dimensions(texture_file_path)

        # if you ran the pixel_grabber we can grab the target pixels without having to load files
        if RUN_PIXEL_GRABBER:
            pixel_to_faces = PixelToFace(TARGET_FILE, texture_max_width, texture_max_height,
                                         preload_STRtree=preload_STRtree,
                                         save_normals=SAVE_NORMALS, save_uvs=SAVE_UVS, disable_target_pixels_load=True)
            pixel_to_faces.pass_in_target_pixels(pixel_grabber.pixels_by_label)
        else:
            pixel_to_faces = PixelToFace(TARGET_FILE, texture_max_width, texture_max_height,
                                         preload_STRtree=preload_STRtree,
                                         save_normals=SAVE_NORMALS, save_uvs=SAVE_UVS, disable_target_pixels_load=False)
        # if you ran the geometry files we can pass those in as well
        if not preload_STRtree:
            pixel_to_faces.pass_in_geometry_data(obj_to_json.face_data, obj_to_json.normals_data, obj_to_json.uvs_data)

        end = time.time()
        print()
        print(f"Finished reading in geometries...Took {end - start} seconds")

        start = time.time()
        # create all the points within the obj files
        if RUN_TRIANGLE_DECOMPOSER:
            # then break down those geometry files
            # pixel_to_faces.decompose_all_triangles(texture_max_width, texture_max_height)
            pixel_to_faces.build_str_tree()

        # then search through target_uvs
        pixel_to_faces.find_faces_of_targets(THREAD_COUNT)

        end = time.time()
        print(end - start)
        print(f"Pixel to face search took {(end - start) / 60} minutes")

    ###################################################################################################################
    ### NEW SCRIPT STARTS HERE ###
    if RUN_PIXEL_INDEXER:
        print()
        print("Starting Pixel Indexer and .obj creation")
        start = time.time()
        if RUN_PIXEL_TO_FACE:
            indexer = PixelIndexer(label_names_to_test, pixel_to_faces.label_faces, SAVE_NORMALS, SAVE_UVS)
        else:
            indexer = PixelIndexer(label_names_to_test, save_normals=SAVE_NORMALS, save_uvs=SAVE_UVS)
        end = time.time()
        print()
        print(f"Finished reading in faces...Took {end - start} seconds")
        start = time.time()
        # this creates and writes to file
        indexer.create_indexed_faces()
        # this is to help us for file creation in the web code
        create_file_names_list()
        end = time.time()
        print(end - start)
        print(f"Pixel indexing and file creation took {(end - start) / 60} minutes")
    print()
    print(f"ALL OPERATIONS TOOK: {(end - start0) / 60} minutes")
