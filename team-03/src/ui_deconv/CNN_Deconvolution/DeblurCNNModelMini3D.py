import tensorflow as tf
import keras.backend as K
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.optimizers.experimental import AdamW

class MSETVLoss:
    def __init__(self):
        # define directions to first deriatevies
        self._x_dif = np.array([
            [[-1, 1], [0, 0]],
            [[0, 0], [0, 0]]
        ])
        
        self._y_dif = np.array([
            [[-1, 0], [1, 0]],
            [[0, 0], [0, 0]]
        ])
        
        self._z_dif = np.array([
            [[-1, 0], [0, 0]],
            [[1, 0], [0, 0]]
        ])
        
        filters = [
            self._x_dif,
            self._y_dif,
            self._z_dif,
        ]
        
        self._tf_filters = []
        
        for i_filter in filters:
            filter_shape = i_filter.shape
            tf_filter = i_filter.flatten()[::-1].reshape(filter_shape)  # filter.T
            tf_filter = tf.constant(
                tf_filter.reshape(tf_filter.shape[0], tf_filter.shape[1], tf_filter.shape[2], 1, 1),
                dtype=tf.float32,
            )
            self._tf_filters.append(tf_filter)
            
        pass

    def _mse_tv_loss_function(self, y_true, y_pred, tv_coef):
        results = []
        
        res_x = tf.nn.conv3d(y_pred, self._tf_filters[0], [1, 1, 1, 1, 1], "VALID", "NDHWC")
        res_y = tf.nn.conv3d(y_pred, self._tf_filters[1], [1, 1, 1, 1, 1], "VALID", "NDHWC")
        res_z = tf.nn.conv3d(y_pred, self._tf_filters[2], [1, 1, 1, 1, 1], "VALID", "NDHWC")
        
        l1_grad_norm_reg = tf.math.reduce_mean(tf.math.sqrt(res_x ** 2 + res_y ** 2 + res_z ** 2))
        
        mse_part = tf.keras.losses.MSE(y_true, y_pred)

        return mse_part + l1_grad_norm_reg * tv_coef
    
    def make_loss(self, tv_coef : float):
        def msetv(y_true, y_pred):
            return self._mse_tv_loss_function(y_true, y_pred, tv_coef)
        return msetv
    
class MSEHessianLoss:
    def __init__(self):
        # define directions to first deriatevies
        self._x_dif = np.array([
            [[-1, 1], [0, 0]],
            [[0, 0], [0, 0]]
        ])
        
        self._y_dif = np.array([
            [[-1, 0], [1, 0]],
            [[0, 0], [0, 0]]
        ])
        
        self._z_dif = np.array([
            [[-1, 0], [0, 0]],
            [[1, 0], [0, 0]]
        ])
        
        filters = [
            self._x_dif,
            self._y_dif,
            self._z_dif,
        ]
        
        self._tf_filters = []
        
        for i_filter in filters:
            filter_shape = i_filter.shape
            tf_filter = i_filter.flatten()[::-1].reshape(filter_shape)  # filter.T
            tf_filter = tf.constant(
                tf_filter.reshape(tf_filter.shape[0], tf_filter.shape[1], tf_filter.shape[2], 1, 1),
                dtype=tf.float32,
            )
            self._tf_filters.append(tf_filter)
            
        pass

    def _mse_hessian_loss_function(self, y_true, y_pred, hes_coef):
        results = []
        
        dx = tf.nn.conv3d(y_pred, self._tf_filters[0], [1, 1, 1, 1, 1], "VALID", "NDHWC")
        dx2 = tf.nn.conv3d(dx, self._tf_filters[0], [1, 1, 1, 1, 1], "VALID", "NDHWC")
        dxy = tf.nn.conv3d(dx, self._tf_filters[1], [1, 1, 1, 1, 1], "VALID", "NDHWC")
        dxz = tf.nn.conv3d(dx, self._tf_filters[2], [1, 1, 1, 1, 1], "VALID", "NDHWC")
        
        dy = tf.nn.conv3d(y_pred, self._tf_filters[1], [1, 1, 1, 1, 1], "VALID", "NDHWC")
        dy2 = tf.nn.conv3d(dy, self._tf_filters[1], [1, 1, 1, 1, 1], "VALID", "NDHWC")
        dyz = tf.nn.conv3d(dy, self._tf_filters[2], [1, 1, 1, 1, 1], "VALID", "NDHWC")
        
        dz = tf.nn.conv3d(y_pred, self._tf_filters[2], [1, 1, 1, 1, 1], "VALID", "NDHWC")
        dz2 = tf.nn.conv3d(dz , self._tf_filters[2], [1, 1, 1, 1, 1], "VALID", "NDHWC")
        
        hessian_forbenius_reg = tf.math.sqrt(tf.math.reduce_mean(dx2 ** 2 + dy2 ** 2 + dz2 ** 2 + 2 * dxy ** 2 + 2 * dxz ** 2 + 2 * dyz ** 2) + 0.000025)

        mse_part = tf.keras.losses.MSE(y_true, y_pred)

        return mse_part + hessian_forbenius_reg * hes_coef
    
    def make_loss(self, hes_coef : float):
        def msehess(y_true, y_pred):
            return self._mse_hessian_loss_function(y_true, y_pred, hes_coef)
        return msehess


# Class witch provides CNN training and giving answers
class DeblurCNNModelMini3D:
    def __init__(self):
        return

    def ModelBuilder(input_shape = (64, 64, 40, 1), learning_rate = 0.001, max_value : float = 1, is_need_bias : bool = True):
        enc_channels_1 = 16
        enc_channels_2 = enc_channels_1 * 2
        enc_channels_3 = enc_channels_1 * 4

        enc_channels_4 = enc_channels_1 * 8

        
        # Define the input as a tensor with shape input_shape
        X_input = layers.Input(input_shape, name="img")

        # Stage 1: first Residual layer with (3x3) kernels and (40, 64, 64, *) input_shape
        X_res_con_1 = layers.Conv3D(enc_channels_1, (1, 1, 1), name = 'conv1_0', padding='same', use_bias=is_need_bias)(X_input)
        
        X = layers.Conv3D(enc_channels_1, (3, 3, 3), name = 'conv1_1', padding='same', use_bias=is_need_bias)(X_res_con_1)
        X = layers.BatchNormalization()(X)
        X = layers.LeakyReLU()(X)

        X = layers.Conv3D(enc_channels_1, (3, 3, 3), name = 'conv1_3', padding='same', use_bias=is_need_bias)(X)
        X = layers.BatchNormalization()(X)
        X = layers.Add()([X, X_res_con_1])
        X_1 = layers.LeakyReLU()(X)
        
        X = layers.MaxPooling3D((1, 2, 2))(X_1)
        
        # Stage 2: second Residual layer with (3x3) kernels and (32, 32, 1) input_shape
        X_res_con_2 = layers.Conv3D(enc_channels_2, (1, 1, 1), name = 'conv2_0', padding='same', use_bias=is_need_bias)(X)

        X = layers.Conv3D(enc_channels_2, (3, 3, 3), name = 'conv2_1', padding='same', use_bias=is_need_bias)(X_res_con_2)
        X = layers.BatchNormalization()(X)
        X = layers.LeakyReLU()(X)

        X = layers.Conv3D(enc_channels_2, (3, 3, 3), name = 'conv2_3', padding='same', use_bias=is_need_bias)(X)
        X = layers.BatchNormalization()(X)
        X = layers.Add()([X, X_res_con_2])
        X_2 = layers.LeakyReLU()(X)
        
        X = layers.MaxPooling3D((1, 2, 2))(X_2)

        # Stage 3: third Residual layer with (3x3) kernels and (16, 16, 1) input_shape
        X_res_con_3 = layers.Conv3D(enc_channels_3, (1, 1, 1), name = 'conv3_0', padding='same', use_bias=is_need_bias)(X)
        
        X = layers.Conv3D(enc_channels_3, (3, 3, 3), name = 'conv3_1', padding='same', use_bias=is_need_bias)(X_res_con_3)
        X = layers.BatchNormalization()(X)
        X = layers.LeakyReLU()(X)

        X = layers.Conv3D(enc_channels_3, (3, 3, 3), name = 'conv3_3', padding='same', use_bias=is_need_bias)(X)
        X = layers.BatchNormalization()(X)
        X = layers.Add()([X, X_res_con_3])
        X_3 = layers.LeakyReLU()(X)
        
        X = layers.MaxPooling3D((1, 2, 2))(X_3)

        # Stage 4: fourth Residual layer with (5x5) kernels and (16, 16, 1) input_shape
        X_res_con_4 = layers.Conv3D(enc_channels_4, (1, 1, 1), name = 'conv4_0', padding='same', use_bias=is_need_bias)(X)
        
        X = layers.Conv3D(enc_channels_4, (3, 3, 3), name = 'conv4_1', padding='same', use_bias=is_need_bias)(X_res_con_4)
        X = layers.BatchNormalization()(X)
        X = layers.LeakyReLU()(X)

        X = layers.Conv3D(enc_channels_4, (3, 3, 3), name = 'conv4_3', padding='same', use_bias=is_need_bias)(X)
        X = layers.BatchNormalization()(X)
        X = layers.Add()([X, X_res_con_4])
        X = layers.LeakyReLU()(X)

        # Stage 5: upsampling info from 4th stage
        X = layers.UpSampling3D((1, 2, 2))(X)
        X = layers.Concatenate(axis=-1)([X_3, X])
        
        X_res_con_5 = layers.Conv3D(enc_channels_3, (1, 1, 1), name = 'conv5_0', padding='same', use_bias=is_need_bias)(X)
        
        X = layers.Conv3D(enc_channels_3, (3, 3, 3), name = 'conv5_1', padding='same', use_bias=is_need_bias)(X_res_con_5)
        X = layers.BatchNormalization()(X)
        X = layers.LeakyReLU()(X)

        X = layers.Conv3D(enc_channels_3, (3, 3, 3), name = 'conv5_3', padding='same', use_bias=is_need_bias)(X)
        X = layers.BatchNormalization()(X)
        X = layers.Add()([X, X_res_con_5])
        X = layers.LeakyReLU()(X)

        # Stage 6: upsampling info from 4th stage
        X = layers.UpSampling3D((1, 2, 2))(X)
        X = layers.Concatenate(axis=-1)([X_2, X])

        X_res_con_6 = layers.Conv3D(enc_channels_2, (1, 1, 1), name = 'conv6_0', padding='same', use_bias=is_need_bias)(X)
        
        X = layers.Conv3D(enc_channels_2, (3, 3, 3), name = 'conv6_1', padding='same', use_bias=is_need_bias)(X_res_con_6)
        X = layers.BatchNormalization()(X)
        X = layers.LeakyReLU()(X)

        X = layers.Conv3D(enc_channels_2, (3, 3, 3), name = 'conv6_3', padding='same', use_bias=is_need_bias)(X)
        X = layers.BatchNormalization()(X)
        X = layers.Add()([X, X_res_con_6])
        X = layers.LeakyReLU()(X)

        # Stage 7: upsampling info from 2rd stage
        X = layers.UpSampling3D((1, 2, 2))(X)
        X = layers.Concatenate(axis=-1)([X_1, X])

        X_res_con_7 = layers.Conv3D(enc_channels_1, (1, 1, 1), name = 'conv7_0', padding='same', use_bias=is_need_bias)(X)
        
        X = layers.Conv3D(enc_channels_1, (3, 3, 3), name = 'conv7_1', padding='same', use_bias=is_need_bias)(X_res_con_7)
        X = layers.BatchNormalization()(X)
        X = layers.LeakyReLU()(X)
        
        X = layers.Conv3D(enc_channels_1, (3, 3, 3), name = 'conv7_3', padding='same', use_bias=is_need_bias)(X)
        X = layers.BatchNormalization()(X)
        X = layers.Add()([X, X_res_con_7])
        X = layers.LeakyReLU()(X)

        # Stage 8: final stage
        X_res_con_8 = layers.Conv3D(enc_channels_1, (1, 1, 1), name = 'conv8_1', padding='same', use_bias=is_need_bias)(X)
         
        X = layers.Conv3D(enc_channels_1, (3, 3, 3), name = 'conv8_2', padding='same', use_bias=is_need_bias)(X_res_con_8)
        X = layers.BatchNormalization()(X)
        X = layers.LeakyReLU()(X)

        X = layers.Conv3D(enc_channels_1, (3, 3, 3), name = 'conv8_4', padding='same', use_bias=is_need_bias)(X)
        X = layers.BatchNormalization()(X)
        X = layers.Add()([X_res_con_8, X])
        X = layers.LeakyReLU()(X)

        X = layers.Conv3D(1, (3, 3, 3), name = 'conv8_5', padding='same', use_bias=is_need_bias)(X)
        X_output = layers.BatchNormalization()(X)
        #X = layers.BatchNormalization()(X)
        #X_output = layers.Add()([X, X_input])

        # create loss func
        #loss_func_gen = MSETVLoss()
        loss_func_gen = MSEHessianLoss()
        loss_func = loss_func_gen.make_loss(0.78)
        #loss_func = "mse"
        
        initial_learning_rate = learning_rate
        lr_schedule = initial_learning_rate #tf.keras.optimizers.schedules.ExponentialDecay(initial_learning_rate, decay_steps=12500, decay_rate=0.95, staircase=True)
        
        model = keras.Model(inputs = X_input, outputs = X_output, name='CNNDeconvUNet')
        model.compile(optimizer=Adam(learning_rate=lr_schedule, beta_1=0.9, beta_2=0.999, weight_decay=0.0001),loss=loss_func)
        
        return model
