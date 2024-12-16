import os
import numpy as np
from PIL import Image
from PIL.TiffTags import TAGS


def ReadTiffStackFile(fileName: str, fileInfo = False ,tagID = 270):
    """
    Function ReadTiffStackFile() reads tiff stack from file and return np.array
    Input:
        fileName - path to file
        fileInfo - if true then read tag string and return it
        tagID - tag index
    Returns:
        imgArray : ndarray
        image_tiff.tag[tagID][0] : str
    """
    print("Loading Image from tiff stack file..... ", end=" ")
    try:
        image_tiff = Image.open(fileName)
        # meta_dict = {TAGS[key]:image_tiff.tag[key] for key in image_tiff.tag}
        # print(meta_dict)
        ncols, nrows = image_tiff.size
        nlayers = image_tiff.n_frames
        imgArray = np.ndarray([nlayers, nrows, ncols])
        for i in range(nlayers):
            image_tiff.seek(i)
            imgArray[i, :, :] = np.array(image_tiff)
        print("Done!")
        if fileInfo :
            try:
                return imgArray, image_tiff.tag[tagID][0]
            except:
                return imgArray, ""
        else:
            return imgArray 
    except FileNotFoundError:
        print("ReadTiffStackFile: Error. File not found!")
        return 0




def ReadTiffMultFiles(fileNameList: list):
    """
    Function ReadTiffMultFile() reads tiff stack from file and return np.array
    """
    print("Loading Images from files", end=" ")
    intensity_mult = 10
    try:
        image_preread = Image.open(fileNameList[0])
    except FileNotFoundError:
        print("ReadTiffStackFile: Error. File not found!")
        return 0
    # meta_dict = {TAGS[key]:image_preread.tag[key] for key in image_preread.tag}
    # print(meta_dict)
    print("color_mode:", image_preread.mode, ".......", end=" ")
    nlayers = len(fileNameList)
    ncols, nrows = image_preread.size
    imgArray = np.ndarray([nlayers, nrows, ncols])
    # checking file color mode and convert to grayscale
    if image_preread.mode == "RGB":
        # convert to Grayscale
        for i, fileName in enumerate(fileNameList):
            try: 
                image_tiff = Image.open(fileName)
            except Exception as e:
                print(str(e))
                raise FileNotFoundError
            image_tiff.getdata()
            r, g, b = image_tiff.split()
            ra = np.array(r)
            ga = np.array(g)
            ba = np.array(b)
            grayImgArr = 0.299 * ra + 0.587 * ga + 0.114 * ba
            imgArray[i, :, :] = grayImgArr
            # print("maxint:", i, np.max(grayImgArr))
    elif image_preread.mode == "I" or image_preread.mode == "L":
        for i, fileName in enumerate(fileNameList):
            imgArray[i, :, :] = np.array(Image.open(fileName))
    else:
        print("ReadTiffStackFile: Unsupported file format")
        return
    print("Done.")
    return imgArray


def SaveTiffFiles(tiffDraw=np.zeros([3, 4, 6]), dirName="img", filePrefix=""):
    """Print files for any input arrray of intensity values
    tiffDraw - numpy ndarray of intensity values"""
    layerNumber = tiffDraw.shape[0]
    for i in range(layerNumber):
        im = Image.fromarray(tiffDraw[i, :, :])
        im.save(dirName + "\\" + filePrefix + str(i).zfill(2) + ".tiff")


def SaveTiffStack(
    tiffDraw=np.zeros([3, 4, 6]), dirName="img", filePrefix="!stack", outtype="uint8"
):
    """Print files for any input arrray of intensity values
    tiffDraw - numpy ndarray of intensity values"""
    print("trying to save file", outtype)
    path = os.path.join(dirName, filePrefix)
    imlist = []
    for tmp in tiffDraw:
        #        print(tmp.shape,type(tmp))
        imlist.append(Image.fromarray(tmp.astype(outtype)))

    imlist[0].save(path, save_all=True, append_images=imlist[1:])
    print("file saved in one tiff", path)


def SaveAsTiffStack(tiffDraw=np.zeros([3, 4, 6]), filename="img", outtype="uint8"):
    """Save 3D numpy array as tiff multipage file.
    Input:
    tiffDraw -- 3d numpy ndarray of intensity values
    filename -- name of output file
    outtype -- type of output file ( uint8/16/32)"""
    print(
        "Trying to save tiff file as:",
        filename,
        " color_mode:",
        outtype,
        ".......",
        end=" ",
    )
    imlist = []
    #    try:
    for tmp in tiffDraw:
        imlist.append(Image.fromarray(tmp.astype(outtype)))
    imlist[0].save(filename, save_all=True, append_images=imlist[1:])
    print("Done.")
    # except Exception as e:
    #     print("Not done.")
    #     print("Exception message: ", e)


def SaveAsTiffStack_tag(imgInArray=np.zeros([3, 4, 6]), filename="img", outtype="uint8", tagID = 270, tagString = "Image info"):
    """Print files for any input arrray of intensity values
    tiffDraw - numpy ndarray of intensity values"""
    print("Trying to save file", outtype)
    # test voxel
    # voxelSizeIn = [0.1, 0.022, 0.022]
    # strVoxel = ';'.join(str(s) for s in voxelSizeIn)
    imlist = []
    for tmpArray in imgInArray:
        imlist.append(Image.fromarray(tmpArray.astype(outtype)))
    imlist[0].save(
        filename, tiffinfo={tagID:tagString}, save_all=True, append_images=imlist[1:]
    )
    print("File saved in ", filename)
