import tensorflow as tf
import keras.backend as K
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.optimizers.experimental import AdamW

class SSIMCounter:
    def tf_fspecial_gauss_3d(self, size:int, sigma:float) -> tf.Tensor:
        """Function to mimic the 'fspecial' gaussian MATLAB function"""
        x_data, y_data, z_data = np.mgrid[-size//2 + 1:size//2 + 1, -size//2 + 1:size//2 + 1, -size//2 + 1:size//2 + 1]

        x_data = np.expand_dims(x_data, axis=-1)
        x_data = np.expand_dims(x_data, axis=-1)
        
        y_data = np.expand_dims(y_data, axis=-1)
        y_data = np.expand_dims(y_data, axis=-1)
        
        z_data = np.expand_dims(z_data, axis=-1)
        z_data = np.expand_dims(z_data, axis=-1)
        
        x = tf.constant(x_data, dtype=tf.float32)
        y = tf.constant(y_data, dtype=tf.float32)
        z = tf.constant(z_data, dtype=tf.float32)

        g = tf.exp(-((x**2 + y**2 + z**2)/(2.0*sigma**2)))
        gaussian_filter = g / tf.reduce_sum(g)
        return gaussian_filter

    def __init__(self, 
                 K1:float=0.01, 
                 K2:float=0.03, 
                 L:int=1.125, # +0.125 для запаса?
                 size:int=11, 
                 sigma:float=1.5):
        self.C1 = (K1 * L)**2
        self.C2 = (K2 * L)**2
        self.gaussian_window = self.tf_fspecial_gauss_3d(size, sigma)
        self.zero_tensor = tf.constant(0., dtype=tf.float32)
        pass

    def count_ssim(self, y_true, y_pred):
        y_true = y_true[np.newaxis, ..., np.newaxis]
        y_pred = y_pred[np.newaxis, ..., np.newaxis]
        
        # ssim part
        mu1 = tf.nn.conv3d(y_true, self.gaussian_window, strides=[1,1,1,1,1], padding='VALID')
        mu2 = tf.nn.conv3d(y_pred, self.gaussian_window, strides=[1,1,1,1,1],padding='VALID')
        
        mu1_sq = mu1*mu1
        mu2_sq = mu2*mu2
        mu1_mu2 = mu1*mu2
        
        sigma1_sq = tf.nn.conv3d(y_true*y_true, self.gaussian_window, strides=[1,1,1,1,1],padding='VALID') - mu1_sq
        sigma2_sq = tf.nn.conv3d(y_pred*y_pred, self.gaussian_window, strides=[1,1,1,1,1],padding='VALID') - mu2_sq
        
        sigma12 = tf.nn.conv3d(y_true*y_pred, self.gaussian_window, strides=[1,1,1,1,1],padding='VALID') - mu1_mu2
        value = ((2*mu1_mu2 + self.C1)*(2*sigma12 + self.C2))/((mu1_sq + mu2_sq + self.C1)*
                        (sigma1_sq + sigma2_sq + self.C2))
        ssim = tf.reduce_mean(value)
        
        return ssim
