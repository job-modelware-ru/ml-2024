import tensorflow as tf
import keras.backend as K
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.optimizers.experimental import AdamW

# Class witch provides CNN training and giving answers
class CNNDeconvRescoder:
    def __init__(self):
        return

    def build_model(input_shape = (64, 64, 40, 1), learning_rate : float = 0.001, is_need_bias : bool = False):
        # Original source with tutorial: https://towardsdatascience.com/hitchhikers-guide-to-residual-networks-resnet-in-keras-385ec01ec8ff
        enc_channels_1 = 32
        enc_channels_2 = enc_channels_1 * 2
        enc_channels_3 = enc_channels_2 * 2
        enc_channels_4 = enc_channels_3 * 2

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
        X = layers.LeakyReLU()(X)
        
        X = layers.MaxPooling3D((1, 2, 2))(X)
        
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
        X = layers.LeakyReLU()(X)
        
        X = layers.MaxPooling3D((1, 2, 2))(X)

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
        X = layers.LeakyReLU()(X)
        
        X = layers.MaxPooling3D((1, 2, 2))(X)

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
        print(X.shape)
        X = layers.Conv3DTranspose(enc_channels_3, kernel_size=(1, 2, 2), strides=(1, 2, 2), padding='valid', use_bias=is_need_bias)(X)
        print(X.shape)
        X = layers.LeakyReLU()(X)
        
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
        X = layers.Conv3DTranspose(enc_channels_2, kernel_size=(1, 2, 2), strides=(1, 2, 2), padding='valid', use_bias=is_need_bias)(X)
        X = layers.LeakyReLU()(X)

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
        X = layers.Conv3DTranspose(enc_channels_1, kernel_size=(1, 2, 2), strides=(1, 2, 2), padding='valid', use_bias=is_need_bias)(X)
        X = layers.LeakyReLU()(X)

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
        loss_func = "mae"
        
        initial_learning_rate = learning_rate
        lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(initial_learning_rate, decay_steps=12500, decay_rate=0.95, staircase=True)
        
        
        # weight_decays to check: 0.0001
        # weight_decays checked: 0.01, (2024-03-10_18-03) - bad
        # weight_decays checked: 0.1, (2024-03-11_9-14) - bad
        # weight_decays checked: 0.0030, (2024-03-11_17-45), log(sssim) rewrited to ssim, ssim_coef=1.0, staicase = False, decay_steps=10000, decay_rate=0.8
        # weight_decays checked: 0.001, (2024-03-12_17-01), log(sssim) rewrited to ssim, ssim_coef=0.3, decay_steps=12500, decay_rate=0.8, staircase=True - the best on graphics (!)
        
        model = keras.Model(inputs = X_input, outputs = X_output, name='CNNDeconvResCoder')
        model.compile(optimizer=Adam(learning_rate=lr_schedule, beta_1=0.9, beta_2=0.999, weight_decay=0.001),loss=loss_func)
        
        return model
