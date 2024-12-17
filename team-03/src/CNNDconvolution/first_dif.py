import tensorflow as tf
import numpy as np

class DifCounter:
    def __init__(self):
        
        self.x_dif = np.array([
            [[-1, 1], [0, 0]],
            [[0, 0], [0, 0]]
        ])
        
        self.y_dif = np.array([
            [[-1, 0], [1, 0]],
            [[0, 0], [0, 0]]
        ])
        
        self.z_dif = np.array([
            [[-1, 0], [0, 0]],
            [[1, 0], [0, 0]]
        ])
        
        
        self.xy_dif = np.array([
            [[-1, 0], [0, 1]],
            [[0, 0], [0, 0]]
        ])
        
        self.yz_dif = np.array([
            [[-1, 0], [0, 0]],
            [[0, 0], [1, 0]]
        ])
        
        self.xz_dif = np.array([
            [[-1, 0], [0, 0]],
            [[0, 1], [0, 0]]
        ])
        pass

    def count_first_dif_sum(self, image):
        stock_shape = image.shape
        image = tf.constant(
            image.reshape(1, image.shape[0], image.shape[1], image.shape[2], 1),
            dtype=tf.float32,
        )
        
        filters = [
            self.x_dif,
            self.y_dif,
            self.z_dif,
        ]
        results = []
        
        for i_filter in filters:
        
            filter_shape = i_filter.shape
            filter = i_filter.flatten()[::-1].reshape(filter_shape)  # filter.T
            filter = tf.constant(
                filter.reshape(filter.shape[0], filter.shape[1], filter.shape[2], 1, 1),
                dtype=tf.float32,
            )
            res = tf.nn.conv3d(image, filter, [1, 1, 1, 1, 1], "VALID", "NDHWC")
            
            results.append(np.square(res.numpy().astype("float32").squeeze()))
            
        result = np.sqrt(np.sum(results, axis=0))
        return result 
