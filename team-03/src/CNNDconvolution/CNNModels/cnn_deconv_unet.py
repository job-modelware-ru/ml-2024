import tensorflow as tf
import keras.backend as K
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.optimizers.experimental import AdamW

class SSIMWithMAELoss:
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

    def _mae_and_ssim_loss_function(self, y_true, y_pred, ssim_coef:float):
        mae_part = tf.reduce_mean(tf.abs(y_true - y_pred), axis=-1)

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
        
        min_part = tf.reduce_min(y_pred)

        return mae_part + ssim_coef * (1 - ssim) / 2 #- tf.math.log((1 + ssim) / 2)

    def make_loss(self, ssim_coef : float):
        def mae_ssim(y_true, y_pred):
            return self._mae_and_ssim_loss_function(y_true, y_pred, ssim_coef)
        return mae_ssim


# Class witch provides CNN training and giving answers
class CNNDeconvUNet:
    def __init__(self):
        return

    def build_model(input_shape = (64, 64, 40, 1), learning_rate : float = 0.001, max_value : float = 1, is_need_bias : bool = False):
        # Original source with tutorial: https://towardsdatascience.com/hitchhikers-guide-to-residual-networks-resnet-in-keras-385ec01ec8ff
        enc_channels_1 = 32
        enc_channels_2 = enc_channels_1 * 2
        enc_channels_3 = enc_channels_1 * 4

        enc_channels_4 = enc_channels_1 * 8

        # Define the input as a tensor with shape input_shape
        X_input = layers.Input(input_shape, name="img")

        # Stage 0: lvl-up channels
        X = layers.Conv3D(enc_channels_1, (3, 3, 3), name = 'conv0', padding='same', use_bias=is_need_bias)(X_input)
        X = layers.BatchNormalization()(X)
        X_global_residual = layers.LeakyReLU()(X)
        
        # Stage 1: first Residual layer with (3x3) kernels and (40, 64, 64, *) input_shape
        X_res_con = layers.Conv3D(enc_channels_1, (1, 1, 1), name = 'conv1_0', padding='same', use_bias=is_need_bias)(X_global_residual)
        
        X = layers.Conv3D(enc_channels_1, (3, 3, 3), name = 'conv1_1', padding='same', use_bias=is_need_bias)(X_global_residual)
        X = layers.BatchNormalization()(X)
        X = layers.LeakyReLU()(X)

        #X = layers.Conv3D(enc_channels_1, (3, 3, 3), name = 'conv1_2', padding='same', use_bias=is_need_bias)(X)
        #X = layers.BatchNormalization()(X)
        #X = layers.LeakyReLU()(X)
        
        X = layers.Conv3D(enc_channels_1, (3, 3, 3), name = 'conv1_3', padding='same', use_bias=is_need_bias)(X)
        X = layers.BatchNormalization()(X)
        X = layers.Add()([X, X_res_con])
        X_1 = layers.LeakyReLU()(X)
        
        X = layers.MaxPooling3D((1, 2, 2))(X_1)
        
        # Stage 2: second Residual layer with (3x3) kernels and (32, 32, 1) input_shape
        X_res_con = layers.Conv3D(enc_channels_2, (1, 1, 1), name = 'conv2_0', padding='same', use_bias=is_need_bias)(X)

        X = layers.Conv3D(enc_channels_2, (3, 3, 3), name = 'conv2_1', padding='same', use_bias=is_need_bias)(X)
        X = layers.BatchNormalization()(X)
        X = layers.LeakyReLU()(X)

        #X = layers.Conv3D(enc_channels_2, (3, 3, 3), name = 'conv2_2', padding='same', use_bias=is_need_bias)(X)
        #X = layers.BatchNormalization()(X)
        #X = layers.LeakyReLU()(X)

        X = layers.Conv3D(enc_channels_2, (3, 3, 3), name = 'conv2_3', padding='same', use_bias=is_need_bias)(X)
        X = layers.BatchNormalization()(X)
        X = layers.Add()([X, X_res_con])
        X_2 = layers.LeakyReLU()(X)
        
        X = layers.MaxPooling3D((1, 2, 2))(X_2)

        # Stage 3: third Residual layer with (3x3) kernels and (16, 16, 1) input_shape
        X_res_con = layers.Conv3D(enc_channels_3, (1, 1, 1), name = 'conv3_0', padding='same', use_bias=is_need_bias)(X)
        
        X = layers.Conv3D(enc_channels_3, (3, 3, 3), name = 'conv3_1', padding='same', use_bias=is_need_bias)(X)
        X = layers.BatchNormalization()(X)
        X = layers.LeakyReLU()(X)

        #X = layers.Conv3D(enc_channels_3, (3, 3, 3), name = 'conv3_2', padding='same', use_bias=is_need_bias)(X)
        #X = layers.BatchNormalization()(X)
        #X = layers.LeakyReLU()(X)

        X = layers.Conv3D(enc_channels_3, (3, 3, 3), name = 'conv3_3', padding='same', use_bias=is_need_bias)(X)
        X = layers.BatchNormalization()(X)
        X = layers.Add()([X, X_res_con])
        X_3 = layers.LeakyReLU()(X)
        
        X = layers.MaxPooling3D((1, 2, 2))(X_3)

        # Stage 4: fourth Residual layer with (5x5) kernels and (16, 16, 1) input_shape
        X_res_con = layers.Conv3D(enc_channels_4, (1, 1, 1), name = 'conv4_0', padding='same', use_bias=is_need_bias)(X)
        
        X = layers.Conv3D(enc_channels_4, (3, 3, 3), name = 'conv4_1', padding='same', use_bias=is_need_bias)(X)
        X = layers.BatchNormalization()(X)
        X = layers.LeakyReLU()(X)

        #X = layers.Conv3D(enc_channels_4, (3, 3, 3), name = 'conv4_2', padding='same', use_bias=is_need_bias)(X)
        #X = layers.BatchNormalization()(X)
        #X = layers.LeakyReLU()(X)

        X = layers.Conv3D(enc_channels_4, (3, 3, 3), name = 'conv4_3', padding='same', use_bias=is_need_bias)(X)
        X = layers.BatchNormalization()(X)
        X = layers.Add()([X, X_res_con])
        X = layers.LeakyReLU()(X)

        # Stage 5: upsampling info from 4th stage
        X = layers.UpSampling3D((1, 2, 2))(X)
        X = layers.Concatenate(axis=-1)([X_3, X])
        
        X_res_con = layers.Conv3D(enc_channels_3, (1, 1, 1), name = 'conv5_0', padding='same', use_bias=is_need_bias)(X)
        
        X = layers.Conv3D(enc_channels_3, (3, 3, 3), name = 'conv5_1', padding='same', use_bias=is_need_bias)(X)
        X = layers.BatchNormalization()(X)
        X = layers.LeakyReLU()(X)

        #X = layers.Conv3D(enc_channels_3, (3, 3, 3), name = 'conv5_2', padding='same', use_bias=is_need_bias)(X)
        #X = layers.BatchNormalization()(X)
        #X = layers.LeakyReLU()(X)

        X = layers.Conv3D(enc_channels_3, (3, 3, 3), name = 'conv5_3', padding='same', use_bias=is_need_bias)(X)
        X = layers.BatchNormalization()(X)
        X = layers.Add()([X, X_res_con])
        X = layers.LeakyReLU()(X)

        # Stage 6: upsampling info from 4th stage
        X = layers.UpSampling3D((1, 2, 2))(X)
        X = layers.Concatenate(axis=-1)([X_2, X])

        X_res_con = layers.Conv3D(enc_channels_2, (1, 1, 1), name = 'conv6_0', padding='same', use_bias=is_need_bias)(X)
        
        X = layers.Conv3D(enc_channels_2, (3, 3, 3), name = 'conv6_1', padding='same', use_bias=is_need_bias)(X)
        X = layers.BatchNormalization()(X)
        X = layers.LeakyReLU()(X)

        #X = layers.Conv3D(enc_channels_2, (3, 3, 3), name = 'conv6_2', padding='same', use_bias=is_need_bias)(X)
        #X = layers.BatchNormalization()(X)
        #X = layers.LeakyReLU()(X)

        X = layers.Conv3D(enc_channels_2, (3, 3, 3), name = 'conv6_3', padding='same', use_bias=is_need_bias)(X)
        X = layers.BatchNormalization()(X)
        X = layers.Add()([X, X_res_con])
        X = layers.LeakyReLU()(X)

        # Stage 7: upsampling info from 2rd stage
        X = layers.UpSampling3D((1, 2, 2))(X)
        X = layers.Concatenate(axis=-1)([X_1, X])

        X_res_con = layers.Conv3D(enc_channels_1, (1, 1, 1), name = 'conv7_0', padding='same', use_bias=is_need_bias)(X)
        
        X = layers.Conv3D(enc_channels_1, (3, 3, 3), name = 'conv7_1', padding='same', use_bias=is_need_bias)(X)
        X = layers.BatchNormalization()(X)
        X = layers.LeakyReLU()(X)

        #X = layers.Conv3D(enc_channels_1, (3, 3, 3), name = 'conv7_2', padding='same', use_bias=is_need_bias)(X)
        #X = layers.BatchNormalization()(X)
        #X = layers.LeakyReLU()(X)
        
        X = layers.Conv3D(enc_channels_1, (3, 3, 3), name = 'conv7_3', padding='same', use_bias=is_need_bias)(X)
        X = layers.BatchNormalization()(X)
        X = layers.Add()([X, X_res_con])
        X = layers.LeakyReLU()(X)

        # Stage 8: final stage
        X = layers.Conv3D(enc_channels_1, (3, 3, 3), name = 'conv8_0', padding='same', use_bias=is_need_bias)(X)
        X = layers.BatchNormalization()(X)
        X = layers.Add()([X_global_residual, X])
        X = layers.LeakyReLU()(X)       

        X_res_con = layers.Conv3D(enc_channels_1, (1, 1, 1), name = 'conv8_1', padding='same', use_bias=is_need_bias)(X)
         
        X = layers.Conv3D(enc_channels_1, (3, 3, 3), name = 'conv8_2', padding='same', use_bias=is_need_bias)(X)
        X = layers.BatchNormalization()(X)
        X = layers.LeakyReLU()(X)

        #X = layers.Conv3D(enc_channels_1, (3, 3, 3), name = 'conv8_3', padding='same', use_bias=is_need_bias)(X)
        #X = layers.BatchNormalization()(X)
        #X = layers.LeakyReLU()(X)

        X = layers.Conv3D(enc_channels_1, (3, 3, 3), name = 'conv8_4', padding='same', use_bias=is_need_bias)(X)
        X = layers.BatchNormalization()(X)
        X = layers.Add()([X_res_con, X])
        X = layers.LeakyReLU()(X)

        X = layers.Conv3D(1, (3, 3, 3), name = 'conv8_5', padding='same', use_bias=is_need_bias)(X)
        X = layers.BatchNormalization()(X)
        X_output = layers.ReLU()(X)

        # create loss func
        loss_func_gen = SSIMWithMAELoss(L=max_value)
        #loss_func = loss_func_gen.make_loss(ssim_coef = 0.0)
        loss_func = "mse"
        
        initial_learning_rate = learning_rate
        lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(initial_learning_rate, decay_steps=12500, decay_rate=0.95, staircase=True)
        
        
        # weight_decays to check: 0.0001
        # weight_decays checked: 0.01, (2024-03-10_18-03) - bad
        # weight_decays checked: 0.1, (2024-03-11_9-14) - bad
        # weight_decays checked: 0.0030, (2024-03-11_17-45), log(sssim) rewrited to ssim, ssim_coef=1.0, staicase = False, decay_steps=10000, decay_rate=0.8
        # weight_decays checked: 0.001, (2024-03-12_17-01), log(sssim) rewrited to ssim, ssim_coef=0.3, decay_steps=12500, decay_rate=0.8, staircase=True - the best on graphics (!)
        
        model = keras.Model(inputs = X_input, outputs = X_output, name='CNNDeconvUNet')
        model.compile(optimizer=Adam(learning_rate=lr_schedule, beta_1=0.9, beta_2=0.999, weight_decay=0.001),loss=loss_func)
        
        return model
