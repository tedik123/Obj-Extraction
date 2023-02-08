import json
import time
from os import listdir, getcwd
from os.path import isfile, join
from PixelToFace import PixelToFace
from PixelGrabber import PixelGrabber
from PixelIndexer import PixelIndexer


def create_file_names_list():
    ignore_files = [".gitkeep", "human.obj", "file_list.json"]
    mypath = "outputs/OBJ files/"
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f not in ignore_files]
    # add our actual big human anatomy object to the list as well
    # onlyfiles.append("Anatomy.OBJ")
    for i, file in enumerate(onlyfiles):
        onlyfiles[i] = file.removesuffix(".obj")
    json_object = {"muscle_names": onlyfiles}
    with open("outputs/OBJ files/muscle_list.json", "w") as fh:
        json.dump(json_object, fh)
    print("Creating file/muscle list.")


if __name__ == "__main__":
    # IMPORTANT  this is an array of strings, if it's empty it will do all of them
    muscle_names_to_test = ["Vastus Medialis", "Vastus Lateralis", "Trapezius", "Teres Minor", "Teres Major"]
    # grab last two for testing
    muscle_names_to_test = muscle_names_to_test[-3:]
    muscle_names_to_test = []

    # if there's a fade or variation in color you will want to raise this to loosen what is an acceptable color
    default_pixel_deviation = 0

    # IMPORTANT unless you're testing something you can just leave it
    TARGET_FILE = 'outputs/pixels_by_muscles.json'
    # if you only want to run certain scripts you can change accordingly here
    RUN_PIXEL_GRABBER = True
    RUN_PIXEL_TO_FACE = False
    RUN_PIXEL_INDEXER = False

    start0 = time.time()
    if RUN_PIXEL_GRABBER:
        # first create the object which simply loads in the diffuse.jpg and relevant data
        # also reads in the muscle starts
        pixel_grabber = PixelGrabber(muscle_names_to_test, default_pixel_deviation)
        # then run the actual pixel_grabber algo
        pixel_grabber.run_pixel_grabber()
        # to save the pixels by muscle
        # you can specify an output file name as an argument if you want (optional)
        pixel_grabber.save_pixels_by_muscles()
        # if you are testing, you can visualize the changes with
        # you can specify a specific hex color default is '#000000'
        pixel_grabber.change_pixels_test()

        end = time.time()
        print()
        print(f"Finished finding pixels...Took {end - start0} seconds")

    ###################################################################################################################
    ### NEW SCRIPT STARTS HERE ###
    if RUN_PIXEL_TO_FACE:
        print("Starting pixels to faces code!")
        start = time.time()
        pixel_to_faces = PixelToFace(TARGET_FILE)
        end = time.time()
        print()
        print(f"Finished reading in geometries...Took {end - start} seconds")
        start = time.time()

        # create all the points within the class
        # IMPORTANT you can comment this out if it's already been done!
        # pixel_to_faces.decompose_all_triangles()

        # then search through target_uvs
        pixel_to_faces.find_faces_of_targets()
        end = time.time()
        print(end - start)
        print(f"Pixel to face search took {(end - start) / 60} minutes")

    if RUN_PIXEL_INDEXER:
        ###################################################################################################################
        ### NEW SCRIPT STARTS HERE ###
        print()
        print("Starting Pixel Indexer and .obj creation")
        start = time.time()
        indexer = PixelIndexer(muscle_names_to_test)
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
