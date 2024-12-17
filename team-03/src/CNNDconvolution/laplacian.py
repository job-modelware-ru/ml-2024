import tensorflow as tf
import numpy as np

class Laplacian:
    def __init__(self):
        
        self.laplaccian_1 = np.array([
            [[0, 0, 0], [0, 1, 0], [0, 0, 0]],
            [[0, 1, 0], [1, -6, 1], [0, 1, 0]],
            [[0, 0, 0], [0, 1, 0], [0, 0, 0]],
        ])
        print(self.laplaccian_1.shape)
        
        self.laplaccian_2 = np.array([
            [[1, 1, 1], [1, 1, 1], [1, 1, 1]],
            [[1, 1, 1], [1, -26, 1], [1, 1, 1]],
            [[1, 1, 1], [1, 1, 1], [1, 1, 1]],
        ])
        print(self.laplaccian_2.shape)
        pass

    def count_laplaccian(self, image, lapl_type = 1):
        stock_shape = image.shape
        image = tf.constant(
            image.reshape(1, image.shape[0], image.shape[1], image.shape[2], 1),
            dtype=tf.float32,
        )
        
        if lapl_type == 1:
            filter = self.laplaccian_1
        else:
            filter = self.laplaccian_2
        
        filter_shape = filter.shape
        filter = filter.flatten()[::-1].reshape(filter_shape)  # filter.T
        filter = tf.constant(
            filter.reshape(filter.shape[0], filter.shape[1], filter.shape[2], 1, 1),
            dtype=tf.float32,
        )
        res = tf.nn.conv3d(image, filter, [1, 1, 1, 1, 1], "VALID", "NDHWC")
        return res.numpy().astype("float32").squeeze()
