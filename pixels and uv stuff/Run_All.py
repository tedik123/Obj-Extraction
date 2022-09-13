import time

from PixelToFace import PixelToFace
from PixelGrabber import PixelGrabber
from PixelIndexer import PixelIndexer

if __name__ == "__main__":
    # IMPORTANT  this is an array of strings, if it's empty it will do all of them
    muscle_names_to_test = []
    # IMPORTANT unless you're testing something you can just leave it
    TARGET_FILE = 'outputs/pixels_by_muscles.json'

    start0 = time.time()
    # first create the object which simply loads in the diffuse.jpg and relevant data
    # also reads in the muscle starts
    pixel_grabber = PixelGrabber(muscle_names_to_test)
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
    end = time.time()
    print(end - start)
    print(f"Pixel indexing and file creation took {(end - start) / 60} minutes")
    print()
    print(f"ALL OPERATIONS TOOK: {(end - start0) / 60} minutes")



