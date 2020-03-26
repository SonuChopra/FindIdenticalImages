# FindIdenticalImages
 My dad was looking for a quick way to find all identical images in a folder and delete them. This is a simple and quick python script I wrote to parse all the images inside of a folder and find the identical images. It lets you choose between keeping or deleting the identical image.
 
 The script starts by asking you what folder you would like to analyze for identical images. The script will parse throw all files, even if they are in a subfolder, in the folder. Then it hashes each images one by one and stores it in a database table (sqlite3). After doing so, it shows the user the images with the same hash. Then the user decides what images he/she would like to keep or get rid of. The script DOES NOT actually delete the image. It just moves them to a folder called delete. Which is created where ever the script is downloaded and run from.

In order to use the program follow the following steps:
- Make sure you have python3 downloaded
- After python 3 is installed you should install Pillow and Imagehash using the following commands:
    *`pip3 install Pillow`
    *`pip3 install ImageHash`

- To run the program, simply cd to where the FindIdenticalImages file is located in your terminal and type:
- `python3 FindIdenticalImages.py`

 LINK TO DEMO VIDEO: https://drive.google.com/file/d/11hb2nxH0S7cqxUjbtZblcKqwwzUnnOV4/view?usp=sharing


 Features to add:
 - If two subfolders, and the images and files within each subfolder, are completely identical, give the option to delete the entire folder
 - Have the option to automatically delete all duplicate images

