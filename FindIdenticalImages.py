#imports
import sqlite3
from tkinter import *
from tkinter.ttk import Progressbar
from PIL import Image
from PIL import ImageFile
from PIL import ImageTk
import imagehash
import os
import shutil
import imghdr
import threading
import tkinter
from tkinter import filedialog
from pathlib import Path
import datetime

# global variables
root = 0
c = 0 # cursor
conn = 0
listOfImagesWithTheSameHash = []
listOfImagesWithTheSameHashIndex = 0
pathOfImagesToDelete = []

# if delete is clicked then add to path to pathOfImagesToDelete
# if it already exists in pathOfImagesToDelete then remove from pathOfImagesToDelete
# reload page
def addToPathOfImagesToDelete(path):
    global pathOfImagesToDelete
    global listOfImagesWithTheSameHashIndex
    global listOfImagesWithTheSameHash

    if path in pathOfImagesToDelete:
        pathOfImagesToDelete.remove(path)
    else:
        pathOfImagesToDelete.append(path)
    loadImagesSideBySide()

# when next button is clicked show next images
def showNextImages():
    global listOfImagesWithTheSameHashIndex
    listOfImagesWithTheSameHashIndex = listOfImagesWithTheSameHashIndex + 1
    showImagesSideBySide()

# reload all images that are currently being indexed
def loadImagesSideBySide():
    global listOfImagesWithTheSameHashIndex
    global listOfImagesWithTheSameHash
    global root
    global pathOfImagesToDelete

    row = 0
    for widget in root.winfo_children():
        widget.destroy()
    
    for index, path in enumerate(listOfImagesWithTheSameHash[listOfImagesWithTheSameHashIndex]):
        
        # opening image, if image is selected to be deleted then make black and white
        openImage = Image.open(path)
        if path in pathOfImagesToDelete:
            openImage = openImage.convert('LA')

        # resizing images
        h1, w1 = openImage.size
        maxSize = int(800/len(listOfImagesWithTheSameHash[listOfImagesWithTheSameHashIndex]))
        scale = 1.1
        while(h1 > maxSize or w1 > maxSize):
            h1 = int(h1/scale)
            w1 = int(w1/scale)
        openImage = openImage.resize((h1, w1), Image.ANTIALIAS)

        # displaying path of each image
        textFilePath = str(path)
        labelSelectAFolder = Label(root, text=textFilePath)
        labelSelectAFolder.grid(row=row, column=0)

        # displaying image itself
        renderImage = ImageTk.PhotoImage(openImage)
        img = Label(root, image=renderImage)
        img.image = renderImage
        img.grid(row=(row+1), column=0)
        
        # changing button text when clicked
        deleteBtnText = "Delete"
        if path in pathOfImagesToDelete:
            deleteBtnText = "Dont Delete"

        btnDeleteImg = Button(root, text=deleteBtnText, command=lambda currPath=path: addToPathOfImagesToDelete(currPath))
        btnDeleteImg.config( height = 3, width = 9)
        btnDeleteImg.grid(row=(row+1), column=2)
        row = row + 2

    btnnext = Button(root, text="Next", command=lambda: showNextImages())
    btnnext.config( height = 12, width = 8)
    btnnext.place(relx=1, rely=0.5, anchor=SE)

# take all paths of images in pathOfImagesToDelete
# move them to delete folder with unizue name
def cleanUp():
    global root
    global pathOfImagesToDelete
    global conn
    DELETE_FOLDER_LOCATION = "./delete/"
    count = 0

    # destroy window
    root.destroy()
    for path in pathOfImagesToDelete:
        currentDateTime = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        shutil.move(path, DELETE_FOLDER_LOCATION)
        oldFileName = str(os.path.basename(str(path)))
        (file, ext) = os.path.splitext(os.path.basename(str(path)))
        newFileName = str(file) + str(currentDateTime) + "_" + str(count) + str(ext)
        count = count + 1
        os.rename(os.path.join(DELETE_FOLDER_LOCATION, oldFileName), os.path.join(DELETE_FOLDER_LOCATION, newFileName))
    conn.close()
    print("... ended")

# if no more comparisons are left, then cleanup,
# else load next images
def showImagesSideBySide():
    global listOfImagesWithTheSameHashIndex
    global listOfImagesWithTheSameHash
    
    if len(listOfImagesWithTheSameHash) <= listOfImagesWithTheSameHashIndex:
        cleanUp()
    else:
        root.geometry("600x1000")
        loadImagesSideBySide()

# gets all hashes that are not unique in db
# gets path for all images with non unique hashes
# adds these paths to a global variable
def getSameImagesFromDB():
    global root
    global listOfImagesWithTheSameHash

    c.execute("SELECT hash, COUNT(*) FROM pathandhashtb GROUP BY hash HAVING COUNT(*) >= 2")
    nonUniqueHashes = c.fetchall()

    if len(nonUniqueHashes) > 0:
        for hsh in nonUniqueHashes:
            tempPath = []
            c.execute("SELECT path FROM pathandhashtb WHERE hash = ?", (hsh[0], ))
            pathsOfImagesWithSameHash = c.fetchall()

            for path in pathsOfImagesWithSameHash:
                tempPath.append(path[0])
            listOfImagesWithTheSameHash.append(tempPath)
        showImagesSideBySide()
    else:
        for widget in root.winfo_children():
            widget.destroy()

        labelSelectAFolder = Label(root, text="Could not find any identical images in folder")
        labelSelectAFolder.place(relx=0.5, rely=0.5, anchor=CENTER)

        btnClose = Button(root, text="Close", command=lambda: rootDestroy())
        btnClose.config(height=2, width=7)
        btnClose.place(relx=1, rely=1, anchor=SE)


# displays label and progress bar
# store hash and path of each valid image in a db table
# updates progress bar and label as images get hashed
def hashSlashAndStoreWithPath(topFolderPath, numberOfFiles):
    global root
    global c
    global conn
    filesHashed = 0
    ext = ["rgb", "gif", "pbm", "pgm", "ppm", "tiff", "rast", "xbm", "jpeg", "bmp", "png", "webp", "exr"]

    # clear main window
    for widget in root.winfo_children():
        widget.destroy()

    # add label teeling user number of images hashed
    textImagesHashed = "About to begin hashing of images ..."
    labelImagesHashed = Label(root, text=textImagesHashed)
    labelImagesHashed.place(relx=0.5, rely=0.3, anchor=CENTER)

    textFilenameShow = ""
    labelFilenameShow = Label(root, text=textFilenameShow)
    labelFilenameShow.place(relx=0.5, rely=0.7, anchor=CENTER)

    # add progress bar showing number of images hashed
    progressBar = Progressbar(root, orient = HORIZONTAL, 
                length = 350, mode = 'determinate') 
    progressBar.place(relx=0.5, rely=0.5, anchor=CENTER)

    for dirpath, dirs, files in os.walk(topFolderPath):
        for fil in files:
            filename = os.path.join(dirpath,fil)
            if str(imghdr.what(str(filename))) in ext:
                openImage = Image.open(filename)
                c.execute("INSERT INTO pathandhashtb VALUES (?,?)", (str(filename), str(imagehash.average_hash(openImage))))
                openImage.close()
                
                filesHashed = filesHashed + 1
                textImagesHashed = str(filesHashed) + "/" + str(numberOfFiles) + " images hashed"
                labelImagesHashed["text"] = textImagesHashed

                textFilenameShow = str(fil)
                labelFilenameShow["text"] = textFilenameShow

                progressBar['value'] = int((filesHashed/numberOfFiles)*100)
                root.update_idletasks()
                conn.commit()

    getSameImagesFromDB()

def rootDestroy():
    global root
    root.destroy()

# runs after folder is selected from folder dialog pop up
# parses through entire directory to find all suitable images
# counts total number of suitable images
# this is mainly done for the prgress bar when hashing
def setTotalNumberOfFilesToHash(userFolderPath):
    global root
    totalNumberOfFilesToHash = 0
    ext = ["rgb", "gif", "pbm", "pgm", "ppm", "tiff", "rast", "xbm", "jpeg", "bmp", "png", "webp", "exr"]

    for dirpath, dirs, files in os.walk(userFolderPath):
        for fil in files:
            fname = os.path.join(dirpath, fil)
            if str(imghdr.what(str(fname))) in ext:
                totalNumberOfFilesToHash = totalNumberOfFilesToHash + 1
    
    if totalNumberOfFilesToHash > 0:
        hashSlashAndStoreWithPath(userFolderPath, totalNumberOfFilesToHash)
    else:
        for widget in root.winfo_children():
            widget.destroy()

        labelSelectAFolder = Label(root, text="Could not find any images in folder")
        labelSelectAFolder.place(relx=0.5, rely=0.5, anchor=CENTER)

        btnClose = Button(root, text="Close", command=lambda: rootDestroy())
        btnClose.config(height=2, width=7)
        btnClose.place(relx=1, rely=1, anchor=SE)


        

# run when browser button is clicked
# brings up folder dialog pop up so user can select folder
# after folder is selected, runs function to find total number of images
def setUserFolderPath ():
    currdir = os.getcwd()
    userSelectedFolderPath = filedialog.askdirectory(parent=root, initialdir=currdir, title='Please select a directory')
    if len(userSelectedFolderPath) > 0:
        setTotalNumberOfFilesToHash(userSelectedFolderPath)

# create window with browser button
# browser button allows user to select a folder to parse
def createBrowserWindow():
    #create main window
    global root
    root = tkinter.Tk()

    # set size and title of main window
    root.geometry("400x100")
    root.title("Find Identical Images")

    # add text, asking user to select folder
    labelSelectAFolder = Label(root, text="Select a folder with images:")
    labelSelectAFolder.place(relx=0.0, rely=0.0, anchor=NW)

    # add a button to browse a folder
    btnBrowse = Button(root, text="Browse Folder", command=setUserFolderPath)
    btnBrowse.config(height=2, width=11)
    btnBrowse.place(relx=0.5, rely=0.5, anchor=CENTER)

    root.mainloop()

# main function
# initilizes db
# creates delete folder
def main():
    print("Started ...")
    global c
    global conn

    # allowing truncated images to be loaded
    ImageFile.LOAD_TRUNCATED_IMAGES = True

    # remove old db
    if os.path.exists("PHOTOHASH.db"):
        os.remove("PHOTOHASH.db")

    # create new db
    conn = sqlite3.connect("PHOTOHASH.db")

    #create table if it doesnt exist
    c = conn.cursor()
    c.execute("CREATE TABLE pathandhashtb (path text primary key, hash text)")

    #create delete folder if it doesnt exist
    Path("./delete").mkdir(parents=True, exist_ok=True)
    
    #create the main window
    createBrowserWindow()

main()

