import json
import time
from concurrent.futures import ProcessPoolExecutor
from os import listdir
from os.path import isfile, join
from PixelToFace import PixelToFace
from PixelGrabber import PixelGrabber
from PixelIndexer import PixelIndexer
from PixelGrabber import run_change_pixels_test, save_pixels_by_muscles

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
    # muscle_names_to_test = ["Flexor Carpi Ulnaris","Flexor Carpi Radialis","Flexor Digitorum Superficialis","Flexor Digitorum Longus","Gracilis","Gastrocnemius","Iliopsoas","Infraspinatus","Iliotibial Tract","Latissimus Dorsi","Levator Scapulae","Pectineus","Peroneus Longus"]
    #["Flexor Carpi Ulnaris","Flexor Carpi Radialis","Flexor Digitorum Superficialis","Flexor Digitorum Longus","Gracilis","Gastrocnemius","Iliopsoas","Infraspinatus","Iliotibial Tract","Latissimus Dorsi","Levator Scapulae","Pectineus","Peroneus Longus"]

    # muscle_names_to_test = ["Vastus Medialis", "Vastus Lateralis", "Trapezius",
    #                         "Teres Minor", "Teres Major", "Tensor Fasciae Lata",
    #                         "Tibialis Anterior", "Soleus", "Semitendinosus", "Serratus Anterior", "Rectus Abdominis",
    #                         "Rhomboids", "Pronator Teres", "Palmaris Longus"]
    # # grab last two for testing
    # muscle_names_to_test = muscle_names_to_test[-1:]
    muscle_names_to_test = []

    # if there's a fade or variation in color you will want to raise this to loosen what is an acceptable color
    default_pixel_deviation = 3

    # IMPORTANT unless you're testing something you can just leave it
    TARGET_FILE = 'outputs/pixels_by_muscles.json'
    # if you only want to run certain scripts you can change accordingly here
    RUN_PIXEL_GRABBER = True
    RUN_PIXEL_TO_FACE = True
    RUN_PIXEL_INDEXER = True

    start0 = time.time()
    if RUN_PIXEL_GRABBER:
        # first create the object which simply loads in the diffuse.jpg and relevant data
        # also reads in the muscle starts
        pixel_grabber = PixelGrabber(muscle_names_to_test, default_pixel_deviation)
        # allows for a wider white range to capture more of the label, disable it if too aggressive
        # pixel_grabber.disable_wide_white_range()

        # this is for the future processes
        executor = ProcessPoolExecutor(max_workers=2)
        # although this takes forever it is not worth optimizing as it is a task that must be waited on
        # before anything else is run
        pixel_grabber.set_and_create_image_data()

        # creates the range of acceptable colors by muscle
        pixel_grabber.create_acceptable_colors_by_muscle()

        # then run the actual pixel_grabber algo
        pixel_grabber.run_pixel_grabber()

        #  to save the pixels by muscle
        # you can specify an output file name as an argument if you want (optional)
        output_file_name = "pixels_by_muscles.json"
        futures = [executor.submit(save_pixels_by_muscles, pixel_grabber.pixels_by_muscle, output_file_name)]

        # pixel_grabber.save_pixels_by_muscles() # run for better print statements without process pool

        # if you are testing, you can visualize the changes with the change_pixels_test
        # you can specify a specific hex color default is '#000000'
        hex_color = '#000000'
        futures.append(
            executor.submit(run_change_pixels_test, pixel_grabber.texture_file, pixel_grabber.pixels_by_muscle,
                            hex_color))
        # pixel_grabber.change_pixels_test() # run for better print statements without process pool

        executor.shutdown(wait=True, cancel_futures=False)
        print("Finished saving pixel change test file and pixel by muscle.json file")

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
