**The purpose of this is to convert a texture map label to a 3D geometry object based on
the object the texture belongs to. Assuming the original model has a UV map.
The main script is Run_all.py.**


# General

**PixelGrabber** reads in from the label_starts.json file and finds all pixels that match
(in your texture file) the acceptable colors parameter given starting points via depth first search.

**PixelToFace** is by far the most intensive, and returns what faces the texture pixel belongs to.
It begins by creating 3 separate files one for the faces, uvs, and normals. It then decomposes
each triangle into a series of points that are on or within the triangle.
This takes a long time but only needs to be run once (assuming you're using the same base .obj file)
and can be turned off by setting "RUN_TRIANGLE_DECOMPOSER" to false! Subsequent runs are much
faster. Having these files the code can match uvs and pixel coordinates to a particular face.

**PixelIndexer** reads in what PixelToFace finds (the faces) and formats, removes repetitions, 
and ultimately creates the .obj file.

**Run_All** is a container for all the other scripts to simplify the interaction.

For specific runs you can run for specific labels given a list of names.
You can also enable/disable specific scripts by changing the boolean statements to False or True.
![img.png](/misc/label_list_example.png)


# Detailed Steps

These steps should be performed in the Run_All.py file.

### Pixel Grabber

Pixel Grabber is the most important step and consequently has the most setup. It has a variety of 
options most of which you will want to manipulate depending on your texture.
1. The first thing to do is to drop in your texture file (.png, .jpg, .jpeg, etc)
into the "obj textures" folder. 
2. Then you'll want to change the texture_file_path from "texture.jpg"
to whatever your file name is.
![img.png](/misc/texture_file_path.png)
3. Navigate to the starts folder and open the label_starts.json file. It's here you'll want to
add the data for the labels you want.
   1. Label_name is the name of the label and will also be the name when it's turned into a .obj file
   2. Label is a shorthand name for it can be the same or different
   3. Starting_points  are the x,y pixel coordinates (assuming top left is 0,0) where the search will begin for the 
   label collecting all accepted pixels from the surrounding area.
   You can have multiple starts in case the label is split into two separate areas
   4. acceptable_colors_rgb is the rgb values of the label that you want to be included can be any number of rgb values.
   
   **The following are optional and do not need to be in the JSON**

   5. Min_X, min_Y are the lowest acceptable values, basically not allowing the search to go past
   it.
   6. Max_X, max_Y are the max acceptable values, similarly not allowing the search to continue past those values.
   7. Enable_default_range turns off the default acceptable pixels, often times this will be the colors 
   that make up text.
   8. Pixel Deviation loosens the range of ALL acceptable_colors_rgb by creating all combinations
   between +/- the rgb value(s) and pixel deviation. This is useful when there is a fade or
   a variety of similar colors that makeup a label.
 ![img.png](/misc/json_format.png)
   
4. Default_pixel_deviation loosens the range of acceptable colors given any rgb value
and is applied globally to all RGBs, so you do not have to add a pixel_deviation field
to all labels in the json file. Setting it to 0 disables it. Otherwise, it will create
every combination between +/- the pixel deviation and rgb value.
![img.png](/misc/default_pixel_deviation.png)
5. Default_acceptable_colors is a list of rgb values that are **globally** acceptable,
this usually means those colors make up some text inside a label area. It can be left blank.
6. deviation_default_colors only affects the default_acceptable_colors and loosens the range 
of acceptable RGBs. Setting it to 0 turns it off. Otherwise, it will create
every combination between +/- the pixel deviation and rgb value.

To verify if the label was correctly captured, open the "pixel_change_test.png" file inside the "outputs" folder.
This image will display all the captured pixels as black to provide a clear visual indication of the pixels that were selected.

### Pixel To Face
Pixel to face is the most computationally intensive script, and it breaks down an .obj file
into normals, uvs, and faces. It then uses that to figure out what pixel value belongs to which face
and this is how we get our .obj files ultimately.
1. Copy over your .obj file into the "obj files" directory.
2. Base_obj_file_path should be changed to the path of your obj file like this "obj_files/YourFile.obj"
3. You can choose whether the final .obj file should also save the base obj file's uvs and normals by 
setting the SAVE_UVS and SAVE_NORMALS to true or false.
![img.png](/misc/save_normals.png)
4. If this is your first time running this script set RUN_TRIANGLE_DECOMPOSER to True. This only needs
to be run once per base obj file, so if you don't change your obj file all subsequent runs can be done 
with RUN_TRIANGLE_DECOMPOSER to False.


### Pixel Indexer
This creates and cleans up all the .obj files for each label originally provided.
Since it's only cleaning up outputs and creating there are no steps, only that you have run the previous
two scripts at some point.


### Run_All.py
This contains all the other scripts and should be where you run the code.

- Label_names_to_test are the labels you want to run, and it will affect all scripts. 
You can leave it blank and it will run on all your labels in label_starts.json
- You can adjust which scripts run and if the triangle decomposer runs by adjusting the RUN_ variables to false.
![img_1.png](/misc/script%20booleans.png)

Following all the above steps you can run the script to create your label objects!