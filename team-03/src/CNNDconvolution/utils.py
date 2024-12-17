from PIL import Image
import typing as tp
import numpy as np

def load_colorfull_tiff(path : str, color_channel : int | None = None) -> np.ndarray:
    try:
        image = Image.open(path)
        ncols, nrows = image.size
        nlayers =  image.n_frames

        imgArray = np.ndarray([nlayers,nrows,ncols])
        for i in range(nlayers):
            image.seek(i)
            if color_channel != None:
                imgArray[i,:,:] = np.array(image)[..., color_channel]
            else:
                imgArray[i,:,:] = np.array(image)
        return imgArray
    except FileNotFoundError:
        print("ReadTiffStackFile: Error. File not found!")
        return None

def clip_intensivity(img : np.ndarray, low_border : int, high_border : int) -> np.ndarray:
    return np.clip(img, low_border, high_border)

def maximize_intenivity(img : np.ndarray, max_val : int = 255) -> np.ndarray:
    return img / np.amax(img) * max_val

def save_tiff(image_3d:np.ndarray, path : str, color_channel : int | None = None) -> None:
    images_list = []
    for layer in image_3d:
        if color_channel != None:
            color_layer = np.zeros(shape=(*(layer.shape), 3))
            color_layer[:, :, color_channel] = layer[:, :]
            layer = color_layer
        images_list.append(Image.fromarray(layer.astype("uint8")))
    images_list[0].save(path, save_all=True, append_images=images_list[1:])
    return

def plot_in_slices(img:np.ndarray):
    return
