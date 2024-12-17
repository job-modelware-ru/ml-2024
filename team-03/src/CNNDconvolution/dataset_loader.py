import tensorflow as tf
import numpy as np
from random import randint
import math

class DatasetSequence(tf.keras.utils.Sequence):

    def __init__(self, x_set : np.ndarray, y_set : np.ndarray, batch_size : int, isNeedToNoize : bool=True):
        self.__x, self.__y = x_set, y_set
        self.__batch_size = batch_size
        self.__isNeedToNoize = isNeedToNoize

    def __len__(self):
        return math.ceil(len(self.__x) / self.__batch_size)

    def __getitem__(self, idx):
        low = idx * self.__batch_size
        high = min(low + self.__batch_size, len(self.__x))

        batch_x = np.array(self.__x[low:high])
        
        if self.__isNeedToNoize:
            noize_mid = randint(0, 6)
            batch_x = np.sum(
                        [
                            batch_x,
                            (np.random.poisson(
                                noize_mid,
                                batch_x.shape[0] * batch_x.shape[1] * batch_x.shape[2] * batch_x.shape[3] * batch_x.shape[4])
                            .reshape(batch_x.shape)) / 255.0,
                        ],
                        axis=0,
                    ).astype("float32")

        batch_y = np.array(self.__y[low:high])

        return batch_x, batch_y
