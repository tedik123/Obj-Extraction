import json
import time
from concurrent.futures import ProcessPoolExecutor
from os import listdir, getcwd
from os.path import isfile, join
from PixelToFace import PixelToFace
from PixelGrabber import PixelGrabber
from PixelIndexer import PixelIndexer
from PixelGrabber import run_change_pixels_test, save_pixels_by_labels
from ObjFileToJSONFiles import ObjToJSON


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
    # label_names_to_test = ["Flexor Carpi Ulnaris","Flexor Carpi Radialis","Flexor Digitorum Superficialis","Flexor Digitorum Longus","Gracilis","Gastrocnemius","Iliopsoas","Infraspinatus","Latissimus Dorsi","Levator Scapulae","Pectineus","Peroneus Longus"]
    # ["Flexor Carpi Ulnaris","Flexor Carpi Radialis","Flexor Digitorum Superficialis","Flexor Digitorum Longus","Gracilis","Gastrocnemius","Iliopsoas","Infraspinatus","Iliotibial Tract","Latissimus Dorsi","Levator Scapulae","Pectineus","Peroneus Longus"]

    # label_names_to_test = ["Vastus Medialis", "Vastus Lateralis", "Trapezius",
    #                         "Teres Minor", "Teres Major", "Tensor Fasciae Lata",
    #                         "Tibialis Anterior", "Soleus", "Semitendinosus", "Serratus Anterior", "Rectus Abdominis",
    #                         "Rhomboids", "Pronator Teres", "Palmaris Longus"]

    # label_names_to_test = ["Anconeus", "Adductor Longus", "Adductor Magnus", "Abductor Pollicis Longus", "Brachialis", "Biceps Brachii", "Biceps Femoris", "Brachioradialis", "Coracobrachialis", "Deltoid", "Extensor Carpi Radialis Brevis", "Extensor Carpi Radialis Longus", "Extensor Carpi Ulnaris", "Extensor Digitorum", "Extensor Digitorum Longus", "Extensor Digiti Minimi", "External Oblique", "Extensor Pollicis Brevis", "Erector Spinae"]
    # muscle_names_to_test = ["Anconeus", "Adductor Longus", "Adductor Magnus", "Abductor Pollicis Longus", "Brachialis", "Biceps Brachii", "Biceps Femoris", "Brachioradialis", "Coracobrachialis", "Deltoid", "Extensor Carpi Radialis Brevis", "Extensor Carpi Radialis Longus", "Extensor Carpi Ulnaris", "Extensor Digitorum", "Extensor Digitorum Longus", "Extensor Digiti Minimi", "External Oblique", "Extensor Pollicis Brevis", "Erector Spinae"]
    # # grab last two for testing
    # label_names_to_test = label_names_to_test[-2:]

    # label_names_to_test = ["Pectoralis Major", "Deltoid"]
    label_names_to_test = []

    texture_file_path = 'obj textures/diffuse.jpg'
    # define the dimensions of the image
    texture_max_width, texture_max_height = 4096, 4096

    # if there's a fade or variation in color you will want to raise this to loosen what is an acceptable color
    default_pixel_deviation = 3

    # set white as the default acceptable colors
    default_acceptable_colors = [[255, 255, 255]]
    deviation_default_colors = 2

    base_obj_file_path = "obj files/anatomy.OBJ"

    # choose whether to save the uvs and normals, if both are false it will only save the vertices and faces
    SAVE_UVS = False
    SAVE_NORMALS = False

    # by default will use max threads available - 1
    THREAD_COUNT = None

    # if you only want to run certain scripts you can change accordingly here
    RUN_PIXEL_GRABBER = True
    RUN_PIXEL_TO_FACE = True
    RUN_PIXEL_INDEXER = True

    # this triangle decomposer only needs to be run once if the base .obj file is the same! So turn it to false, after!
    RUN_TRIANGLE_DECOMPOSER = False

    # IMPORTANT unless you're testing something you can just leave it
    # target is what pixels we're trying to find
    TARGET_FILE = 'outputs/pixels_by_labels.json'

    start0 = time.time()
    if RUN_PIXEL_GRABBER:
        # first create the object which simply loads in the diffuse.jpg and relevant data
        # also reads in the label starts
        pixel_grabber = PixelGrabber(texture_file_path, label_names_to_test, default_pixel_deviation)

        # allows for a default color range to capture more of the label (if you have it), disable it if too aggressive
        # pixel_grabber.disable_default_color_range()

        # this is for the future processes
        executor = ProcessPoolExecutor(max_workers=2)
        # although this takes forever it is not worth optimizing as it is a task that must be waited on
        # before anything else is run
        pixel_grabber.read_in_image_data()

        # creates the range of acceptable colors by label, in this case just white basically
        pixel_grabber.create_acceptable_colors_by_label(default_acceptable_colors, deviation_default_colors)

        # then run the actual pixel_grabber algo
        pixel_grabber.run_pixel_grabber_C()

        #  to save the pixels by label
        # you can specify an output file name as an argument if you want (optional)
        output_file_name = "pixels_by_labels.json"
        futures = [executor.submit(save_pixels_by_labels, pixel_grabber.pixels_by_label, output_file_name)]

        # pixel_grabber.save_pixels_by_labels() # run for better print statements without process pool

        # if you are testing, you can visualize the changes with the change_pixels_test
        # you can specify a specific hex color default is '#000000'
        hex_color = '#000000'
        futures.append(
            executor.submit(run_change_pixels_test, pixel_grabber.texture_file, pixel_grabber.pixels_by_label,
                            hex_color))
        # pixel_grabber.change_pixels_test() # run for better print statements without process pool

        executor.shutdown(wait=True, cancel_futures=False)
        print("Finished saving pixel change test file and pixel by label.json file")

        end = time.time()
        print()
        print(f"Finished finding pixels...Took {end - start0} seconds")

    ###################################################################################################################
    ### NEW SCRIPT STARTS HERE ###
    if RUN_PIXEL_TO_FACE:
        print("Starting pixels to faces code!")

        start = time.time()
        if RUN_TRIANGLE_DECOMPOSER:
            # we need this to create the geometry files and again only needs
            # to be run once, so it's paired with the triangle decomposer
            obj_to_json = ObjToJSON(base_obj_file_path)
            obj_to_json.read_in_OBJ_file()
            obj_to_json.insert_face_data()
            obj_to_json.create_json_files()

        pixel_to_faces = PixelToFace(TARGET_FILE, preload_STRtree=not RUN_TRIANGLE_DECOMPOSER,
                                     save_normals=SAVE_NORMALS, save_uvs=SAVE_UVS)
        end = time.time()
        print()
        print(f"Finished reading in geometries...Took {end - start} seconds")
        start = time.time()

        # create all the points within the obj files
        if RUN_TRIANGLE_DECOMPOSER:
            # then break down those geometry files
            start_decompose = time.perf_counter()
            # pixel_to_faces.decompose_all_triangles(texture_max_width, texture_max_height)
            pixel_to_faces.decompose_all_triangles_STRTree()
            end = time.perf_counter()
            py_time = (end - start_decompose)
            print("Python triangle decompose time", py_time)

            # start_decompose = time.perf_counter()
            # pixel_to_faces.decompose_all_triangles_Ccode(texture_max_width, texture_max_height)
            # end = time.perf_counter()
            # c_time = (end - start_decompose)
            # print("C++ triangle decompose time", c_time)
            # # print('C code is {}x faster'.format(py_time / c_time))

        # start_normal_search = time.perf_counter()
        # then search through target_uvs
        # pixel_to_faces.find_faces_of_targets()
        pixel_to_faces.find_faces_of_targets_STRTree_threaded(THREAD_COUNT)
        # end = time.perf_counter()
        # pure_time = (end - start_normal_search)
        # print("Pure decompose check", pure_time)

        # this is a little faster than using 5 cores...but still :(
        # it's really bad
        # start_mixed_search = time.perf_counter()
        # pixel_to_faces.find_faces_of_targets_mixed()
        # end = time.perf_counter()
        # mixed_time = (end - start_mixed_search)
        # print("Mixed decompose check", mixed_time)
        # print('Mixed code is {}x faster'.format(pure_time / mixed_time))

        end = time.time()
        print(end - start)
        print(f"Pixel to face search took {(end - start) / 60} minutes")

    ###################################################################################################################
    ### NEW SCRIPT STARTS HERE ###
    if RUN_PIXEL_INDEXER:
        print()
        print("Starting Pixel Indexer and .obj creation")
        start = time.time()
        indexer = PixelIndexer(label_names_to_test, SAVE_NORMALS, SAVE_UVS)
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
