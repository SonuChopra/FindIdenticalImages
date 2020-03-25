# FindIdenticalImages
 My dad was looking for a quick and dirty way to find all identical(copy) images in a folder and delete them (dont worry the program doesnt actually delete the images, it just stores them in a foled called delete). This is a simple and quick python script I wrote to parse all the images inside of a folder and find the identical images. It lets you choose what images you would like to delete and keep with a nice user interface. The script starts by asking you what folder you would like to analyze for same images. The script will parse throw all files, even if they are in a subfolder. Then it hashes each images one by one and stores it in a database table (sqlite3). After doing so, it shows the user the images with the same hash. Then the user decides what images he/she would like to keep or get rid of. The script does not actually delete the image. It just moves them to a folder called delete. Which is created where ever the script id downloaded and run

In order to use this program, I suggest you download python3,
After python 3 is installed you should install Pillow and Imagehash using the following commands

 `pip3 install Pillow`
 `pip3 install ImageHash`

 To run the program, simply cd to where the file is located in your terminal and type

 `python3 main.py`
