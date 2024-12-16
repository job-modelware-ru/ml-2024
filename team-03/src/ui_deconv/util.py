from file_inout import *

if __name__ == "__main__":
    img = ReadTiffStackFile("./ui_deconv/mono_conus1.tif")
    img = img[:, 712:1224, 512:1024]
    SaveTiffStack(img, "", "test_conus.tif")