# main func
import typing as tp
import numpy as np
import matplotlib.cm as cm

from pipeline_provider import Pipeline
from dataset_generator import DatasetGenerator
from image_processing import *
from plotting_utils import *
from utils import *
from spheres_processing import *

from synthetic_images_generator.sticks_generator import *
from synthetic_images_generator.spheres_generator import *

def noize_filtering(img : np.ndarray, gauss_blur_sigma : float = 3.5) -> np.ndarray:
    binarized_img = make_3d_binarization(img, gauss_blur_sigma)
    img[binarized_img == 0] = 0
    return img


def augmentate_imgs(img : np.ndarray, augmentation_cnt : int = 8) -> tp.List[np.ndarray]:
    augmentated_imgs = [img]
    each_piece_augmentate_piece = augmentation_cnt - 1
    
    min_crop_size = 1
    for j in range(each_piece_augmentate_piece):
        along_z_crop = np.random.randint(min_crop_size, img.shape[0])
        min_crop_size = along_z_crop
        new_img = crop_image(img, [along_z_crop, -1, -1])
        
        rotates_cnt = np.random.randint(0, 3) 
        if rotates_cnt != 0:
            new_img = np.rot90(new_img, rotates_cnt, (1, 2))
        augmentated_imgs.append(new_img)
        
    return augmentated_imgs


def generate_pair(img:np.ndarray, blured_bead:np.ndarray, clear_bead:np.ndarray) -> tp.Tuple[np.ndarray]:
    # generate data
    x_data = convolution(img, blured_bead)
    y_data = convolution(img, clear_bead)
        
    return (x_data, y_data)


def variate_intensity(x_data:np.ndarray, y_data:np.ndarray) -> tp.Tuple[np.ndarray]:
    max_value = uniform(0.3, 1.0)
    multipluer = max_value / np.amax(x_data)
    x_data *= multipluer
    y_data *= multipluer
    
    print(f"Blured sum: {np.sum(x_data)}, Clear sum: {np.sum(y_data)}, Blured max: {np.max(x_data)},  Clear max: {np.max(y_data)}")

    return (x_data, y_data)


def image_loading_and_slicing(path : str, image_split_shape : tp.Tuple[int]) ->tp.List[np.ndarray]:
    # load image
    img = load_tiff(path)
    
    # binarize to find places where could be usefull structures and no background
    binarized_img = make_3d_binarization(img, gauss_blur_sigma = 3.5)
    binarized_img_pieces = np.array(split_image(binarized_img,
        min(image_split_shape[2], binarized_img.shape[2]), 
        min(image_split_shape[1], binarized_img.shape[1]), 
        min(image_split_shape[0], binarized_img.shape[0])))
    # select pieces which contains some info
    pieces_sums = np.array([np.sum(piece) for piece in binarized_img_pieces])
    pieces_indxs = np.where(pieces_sums > 0)
    
    # remove noizes...
    img[binarized_img == 0] = 0
    # ...blur original image...
    img = gaus_blurring(img, gaussian_sigma = 1)
    # ..and split it..
    img_pieces = np.array(split_image(img,
        min(image_split_shape[2], img.shape[2]), 
        min(image_split_shape[1], img.shape[1]), 
        min(image_split_shape[0], img.shape[0])))
    # ...and select some pieces with info
    img_pieces = img_pieces[pieces_indxs]
    print(img_pieces.shape)
    img_pieces = [piece for piece in img_pieces]
    print(len(img_pieces), img_pieces[0].shape)
    return img_pieces


def save_results(x_data:np.ndarray, y_data:np.ndarray) -> tp.Tuple[np.ndarray]:
    if not hasattr(save_results, "counter"):
        save_results.counter = 0  # it doesn't exist yet, so initialize it

    save_tiff((x_data * 255).astype("uint8"), f"./res/blured/{save_results.counter}.tiff")
    save_tiff((y_data * 255).astype("uint8"), f"./res/clear/{save_results.counter}.tiff")

    save_results.counter += 1

    return (x_data, y_data)


def main():
    # init constants for dataset
    IMG_SPLIT_SHAPE = (26, 112, 112)
    DATA_SHAPE = (32, 144, 144) 
    
    # init blured and clear spheres
    SPHERES_PATH = "./DataGeneration/data/spheres_images/22.22.100_200nm_green"
    BEAD_SHAPE = [31, 63, 63]
    Z_SCALE, X_SCALE, Y_SCALE = 0.1, 0.022, 0.022
    BEAD_DIAMETER = 0.2

    gauss_blur_sigma = 1.5
    blured_bead, clear_bead = generate_average_bead_pair(SPHERES_PATH, BEAD_SHAPE, BEAD_DIAMETER, Z_SCALE, X_SCALE, Y_SCALE, low_border=1, gauss_blur_sigma=gauss_blur_sigma)

    # normalize for using as filters
    print(np.sum(blured_bead), np.sum(clear_bead), np.max(blured_bead), np.max(clear_bead))
    blured_bead /= np.sum(blured_bead)
    clear_bead /= np.sum(clear_bead)
    print(np.sum(blured_bead), np.sum(clear_bead))

    # init dataset generator
    dg = DatasetGenerator("shrinked_data", DATA_SHAPE)
    dg.dump_data_info()

    methods_list = [
        lambda path : image_loading_and_slicing(path, IMG_SPLIT_SHAPE),
        lambda img: inflate_image(img, DATA_SHAPE),
        lambda img: [img] if np.sum(img) > 0 else [],                               # filter in pipeline
        lambda img: augmentate_imgs(img, augmentation_cnt=4),
        lambda img : generate_pair(img, blured_bead, clear_bead),
        lambda x_data, y_data : variate_intensity(x_data, y_data),
        lambda x_data, y_data : save_results(x_data, y_data),
        lambda x_data, y_data : dg.append(x_data, y_data) 
    ]

    # images paths
    paths = ["./DataGeneration/data/raw_neurons/21.tiff",
        "./DataGeneration/data/raw_neurons/23.tiff",
        "./DataGeneration/data/raw_neurons/24.tiff",
        "./DataGeneration/data/raw_neurons/29.tiff"]

    pipeline = Pipeline(methods_list)
    for path in paths:
        pipeline(path) 
    dg.dump_data_info()
    dg.close()

    return

def generate_spheres():
    spheres_image_gen = SpheresGenerator()
    spheres_image_gen.init_params(radius_int=[1, 4], brightness_int=[0.5, 1.])
    img = spheres_image_gen.generate_image([32, 1024, 1024], 512)
    save_tiff((img / np.amax(img) * 255).astype("uint8"), "test_spheres.tiff")
    return

def generate_sticks():
    sticks_image_gen = SticksGenerator()
    sticks_image_gen.init_params(radius_int=[1, 6], 
                                brightness_int=[0.3, 1.], omega_int=[-np.pi / 3000, np.pi / 3000])
    img = sticks_image_gen.generate_image([32, 1024, 1024], 40)
    save_tiff((img / np.amax(img) * 255).astype("uint8"), "test_sticks.tiff")
    
    return

def generate_noise():
    sticks_image_gen = SticksGenerator()
    sticks_image_gen.init_params(radius_int=[1, 4], 
                                brightness_int=[0.3, 1.], omega_int=[-np.pi / 200, np.pi / 200])
    img = sticks_image_gen.generate_image([32, 1024, 1024], 15)
    
    for i in [0, 3, 5, 10]:
        noizy_img = add_poisson_noise(img, i)
        save_tiff((noizy_img / np.amax(noizy_img) * 255).astype("uint8"), f"synthetic_sticks_{i}.tiff")
        plot_image_slices(noizy_img, "./", f"jet_synthetic_sticks_{i}.tiff", cm.jet, 0.022, 0.1, np.unravel_index(np.argmax(noizy_img, axis=None), noizy_img.shape), None)
    return

if __name__ == "__main__":
    generate_spheres()
    generate_sticks()
    # generate_noise()
    # main()
