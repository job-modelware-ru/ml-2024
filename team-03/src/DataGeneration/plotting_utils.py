import numpy as np
import typing as tp
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import AxesGrid


def get_row_plane(img : np.ndarray, row : int) -> np.ndarray:
    layers, rows, cols = img.shape[0], img.shape[1], img.shape[2]
    plane = np.ndarray([layers, cols])
    plane[:, :] = img[:, row, :]
    return plane


def get_col_plane(img : np.ndarray, column : int) -> np.ndarray:
    layers, rows, cols = img.shape[0], img.shape[1], img.shape[2]
    plane = np.ndarray([layers, rows])
    plane[:, :] = img[:, :, column]
    return plane


def get_layer_plane(img:np.ndarray, layer:int)->np.ndarray:
    layers, rows, cols = img.shape[0], img.shape[1], img.shape[2]
    plane = np.ndarray([rows, cols])
    plane[:, :] = img[layer, :, :]
    return plane

def generate_image_slices(
    img : np.ndarray,
    cmap,
    xy_resolution:float,
    z_resolution:float,
    coords:tp.Tuple[int]=[0, 0, 0],
    scale_borders:tp.Tuple[int] | None = None
) -> None:
    plane_row, plane_col, plane_layer = (
        get_row_plane(img, coords[1]),
        get_col_plane(img, coords[2]),
        get_layer_plane(img, coords[0]),
    )
    
    if scale_borders == None:
        scale_borders = [0, 0]
        scale_borders[0] = min(
            np.amin(plane_row), np.amin(plane_layer), np.amin(plane_col)
        )
        scale_borders[1] = max(
            np.amax(plane_row), np.amax(plane_layer), np.amax(plane_col)
        )

    aspect_value_xz = z_resolution / xy_resolution#(img.shape[0] * z_resolution) / (img.shape[1] * xy_resolution) * 2
    aspect_value_yz = xy_resolution / z_resolution#(img.shape[2] * xy_resolution) / (img.shape[0] * z_resolution) / 2

    plt_width = (np.array(img).shape[0] + np.array(img).shape[2]) / 25
    plt_height = (np.array(img).shape[0] + np.array(img).shape[1]) / 25
    fig = plt.figure(figsize=(plt_width, plt_height))

    grid = AxesGrid(
        fig,
        111,
        nrows_ncols=(2, 2),
        axes_pad=0.05,
        cbar_mode="single",
        cbar_location="right",
        cbar_pad=0.1,
    )

    grid[0].set_axis_off()

    grid[1].set_axis_off()
    grid[1].set_label("X-Z projection")
    im_main = grid[1].imshow(
        plane_row,
        cmap=cmap,
        vmin=scale_borders[0],
        vmax=scale_borders[1],
        aspect=(aspect_value_xz),
    )

    grid[2].set_axis_off()
    grid[2].set_label("Y-Z projection")
    plane_col = plane_col.transpose()
    im = grid[2].imshow(
        plane_col,
        cmap=cmap,
        vmin=scale_borders[0],
        vmax=scale_borders[1],
        aspect=aspect_value_yz,
    )

    grid[3].set_axis_off()
    grid[2].set_label("X-Y projection")
    im_main = grid[3].imshow(
        plane_layer, cmap=cmap, vmin=scale_borders[0], vmax=scale_borders[1]
    )

    cbar = grid.cbar_axes[0].colorbar(im_main)
    return

def plot_image_slices(
    img : np.ndarray,
    cmap,
    xy_resolution:float,
    z_resolution:float,
    coords:tp.Tuple[int]=[0, 0, 0],
    scale_borders:tp.Tuple[int] | None = None
) -> None:
    generate_image_slices(img, cmap, xy_resolution, z_resolution, coords, scale_borders)
    plt.show()
    return

def save_image_slices(
    img : np.ndarray,
    save_path : str,
    cmap,
    xy_resolution:float,
    z_resolution:float,
    coords:tp.Tuple[int]=[0, 0, 0],
    scale_borders:tp.Tuple[int] | None = None
) -> None:
    generate_image_slices(img, cmap, xy_resolution, z_resolution, coords, scale_borders)
    plt.savefig(save_path)
    return

def center_intensities_show(bead : np.ndarray):
    fig, axes = plt.subplots(1, 3)
    center = np.array(bead.shape) // 2

    fig.suptitle('Intensities sphere')
    axes[0].plot(bead[center[0], center[1], :])
    axes[1].plot(bead[:,center[1], center[2]])
    axes[2].plot(bead[center[0],:,center[2]])
    print(f"x length={np.count_nonzero(bead[center[0],:,center[2]])}px, y length={np.count_nonzero(bead[center[0], center[1], :])}px, z length={np.count_nonzero(bead[:,center[1], center[2]])}px")
    print(bead[:,center[1], center[2]])
    return fig, axes
