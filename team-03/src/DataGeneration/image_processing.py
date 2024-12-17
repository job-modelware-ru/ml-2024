# Class which provides different images processing functions

import numpy as np
from scipy.ndimage.filters import median_filter, gaussian_filter
from scipy.ndimage.morphology import binary_closing, binary_opening
import tensorflow as tf


def split_image(big_image : np.ndarray, 
                img_size_col : int, 
                img_size_row : int, 
                img_size_layer : int) -> list():
    # split by cols
    indxs = np.arange(
        img_size_col,
        big_image.shape[2],
        img_size_col,
        )
    splited_images = np.split(big_image, indxs, axis=2)

    # split by rows
    tmp_res = []
    for img in splited_images:
        indxs = np.arange(
            img_size_row,
            big_image.shape[1],
            img_size_row,
        )
        tmp_res += np.split(img, indxs, axis=1)

    # split by layers
    res = []
    for img in tmp_res:
        indxs = np.arange(
            img_size_layer,
            big_image.shape[0],
            img_size_layer,
        )
        res += np.split(img, indxs, axis=0)

    # remain only images, which have specific shape
    res = list(
        filter(
            lambda x: x.shape[0] == img_size_layer
            and x.shape[1] == img_size_row
            and x.shape[2] == img_size_col,
            res,
        )
    )
    return res


def inflate_image(image : np.ndarray, new_shape : tuple) -> np.ndarray:
    res = []

    (pad_layers, pad_rows, pad_cols) = (
        np.array(new_shape) - np.array(image.shape)
    ) // 2

    z_odd = image.shape[0] % 2
    x_odd = image.shape[1] % 2
    y_odd = image.shape[2] % 2

    new_img = np.pad(
        image,
        [
            (pad_layers, pad_layers + z_odd),
            (pad_rows, pad_rows + x_odd),
            (pad_cols, pad_cols + y_odd),
        ],
        mode="constant",
        constant_values=0,
    )
        
    return new_img


def crop_image(img:np.ndarray, crop_size=[-1, -1, -1]) -> np.ndarray:
    # 'crop_size' - variable with non-zero elements in sizes in format ['depth_size', 'row_size', 'col_size'] 
    img_shape = img.shape
    img_max_pos = np.unravel_index(img.argmax(), img.shape)

    starts = [0, 0, 0]
    ends = [img_shape[0], img_shape[1], img_shape[2]]
    
    for i in range(len(crop_size)):
        if crop_size[i] <= 0:
            starts[i], ends[i] = 0, img_shape[i]
        else:
            starts[i] = max(img_max_pos[i] - crop_size[i] // 2, 0)
            ends[i] = min(img_max_pos[i] + (crop_size[i] + 1) // 2, img_shape[i]) # '+1' in crop_size

            if starts[i] == 0:
                ends[i] = min(crop_size[i], img_shape[i])
            if ends[i] == img_shape[i]:
                starts[i] = max(img_shape[i] - crop_size[i], 0)    

    new_img = np.zeros_like(img)
    new_img[starts[0]:ends[0], starts[1]:ends[1], starts[2]:ends[2]] = img[starts[0]:ends[0], starts[1]:ends[1], starts[2]:ends[2]]
    return new_img

def move_frame(img:np.ndarray, shifts=[0, 0, 0]) -> np.ndarray:
    # 'crop_size' - variable with non-zero elements in sizes in format ['depth_size', 'row_size', 'col_size'] 
    img_shape = img.shape
    img_max_pos = np.unravel_index(img.argmax(), img.shape)

    new_img = img
    for i in range(len(shifts)):
        new_img = np.roll(new_img, shifts[i], i)
    
    if shifts[0]>0:
        new_img[:shifts[0], :, :] = 0
    elif shifts[0]<0:
        new_img[shifts[0]:, :, :] = 0
    
    if shifts[1]>0:
        new_img[:, :shifts[1], :] = 0
    elif shifts[1]<0:
        new_img[:, shifts[1]:, :] = 0
    
    if shifts[2]>0:
        new_img[:, :, :shifts[2]] = 0
    elif shifts[2]<0:
        new_img[:, :, shifts[2]:] = 0
        
    return new_img


def gaus_blurring(image : np.ndarray, gaussian_sigma : int) -> np.ndarray:
    image = gaussian_filter(image, sigma=gaussian_sigma)
    return image


def median_blurring(image : np.ndarray, size_tuple) -> np.ndarray:
    image = median_filter(image, size=size_tuple)
    return image


def local_threshold_3d(image: np.ndarray, base_threshold: int = 10,
                       weight: float = 0.05, block_size: int = 3) -> np.ndarray:
    local_median = median_filter(image, size=block_size)
    threshold = base_threshold - weight * (base_threshold - local_median)
    output = np.zeros_like(image)
    output[image > threshold] = 255

    return output


def make_3d_binarization(img : np.ndarray, gauss_blur_sigma : int = None) -> np.ndarray:
    # make binary mask
    img = img / np.amax(img) * 255.
    
    if gauss_blur_sigma != None:
        img = gaussian_filter(img, sigma=gauss_blur_sigma)
    
    binary_mask = local_threshold_3d(img)

    # make binary closing
    binary_mask = binary_closing(binary_mask, iterations=1).astype("uint8") * 255

    # return mask
    return binary_mask


def image_maximization(image:np.ndarray, max_value:int=255) -> np.ndarray:
    return image / (np.max(image) - np.min(image)) * max_value


def convolution(image : np.ndarray, 
                filter : np.ndarray) -> np.ndarray:
    stock_shape = image.shape
    image = tf.constant(
        image.reshape(1, image.shape[0], image.shape[1], image.shape[2], 1),
        dtype=tf.float32,
    )
    filter_shape = filter.shape
    filter = filter.flatten()[::-1].reshape(filter_shape)  # filter.T
    filter = tf.constant(
        filter.reshape(filter.shape[0], filter.shape[1], filter.shape[2], 1, 1),
        dtype=tf.float32,
    )
    res = tf.nn.conv3d(image, filter, [1, 1, 1, 1, 1], "SAME", "NDHWC")
    return res.numpy().astype("float32").reshape(stock_shape)


def draw_mask_in_position(orig_img : np.ndarray, 
                        brush_mask : np.ndarray, 
                        coord : np.ndarray, 
                        brush_center : np.ndarray):
    brush_start = [
        int(coord[i] - brush_center[i]) for i in range(len(brush_mask.shape))
    ]

    l_low, l_high = max(0, -brush_start[0]), min(
        brush_mask.shape[0], orig_img.shape[0] - brush_start[0]
    )
    r_low, r_high = max(0, -brush_start[1]), min(
        brush_mask.shape[1], orig_img.shape[1] - brush_start[1]
    )
    c_low, c_high = max(0, -brush_start[2]), min(
        brush_mask.shape[2], orig_img.shape[2] - brush_start[2]
    )

    l_low_shifted, l_high_shifted = brush_start[0] + l_low, brush_start[0] + l_high
    r_low_shifted, r_high_shifted = brush_start[1] + r_low, brush_start[1] + r_high
    c_low_shifted, c_high_shifted = brush_start[2] + c_low, brush_start[2] + c_high

    orig_img[
        l_low_shifted:l_high_shifted,
        r_low_shifted:r_high_shifted,
        c_low_shifted:c_high_shifted,
    ] += brush_mask[l_low:l_high, r_low:r_high, c_low:c_high]

    return orig_img

def center_by_intensivity(img : np.ndarray) -> np.ndarray:
    new_img = np.zeros_like(img)
    new_img = draw_mask_in_position(new_img, img, np.array(new_img.shape) // 2, np.argwhere(img == np.amax(img))[0])
    return new_img

def add_poisson_noise(img : np.ndarray, lambda_val : int) -> np.ndarray:
    return np.sum([
                    img,
                    (
                        np.random.poisson(
                            lambda_val,
                            np.prod(img.shape),
                        )
                        .reshape(img.shape)
                        .astype("float32")
                    ),
                ],
                axis=0,
            ).astype("float32")
