import tensorflow as tf
from keras import backend as K
from keras import initializers
from keras.layers import (BatchNormalization, Conv2D, DepthwiseConv2D, PReLU, Flatten,
                          add, Activation, GlobalAveragePooling2D, GlobalMaxPooling2D, Multiply, Concatenate, Lambda, Reshape, Add, Dense, Dropout)

def conv_block(inputs, filters, kernel_size, strides, padding):
    x = Conv2D(filters, kernel_size, strides=strides, padding=padding, use_bias=False,
               kernel_initializer=initializers.random_normal(stddev=0.1),
               bias_initializer='zeros')(inputs)
    x = BatchNormalization(axis=-1, epsilon=1e-5)(x)
    x = PReLU(alpha_initializer=initializers.constant(0.25), shared_axes=[1, 2])(x)
    return x

def depthwise_conv_block(inputs, filters, kernel_size, strides):
    x = DepthwiseConv2D(kernel_size, strides=strides, padding="same", use_bias=False,
                        depthwise_initializer=initializers.random_normal(stddev=0.1),
                        bias_initializer='zeros')(inputs)
    x = BatchNormalization(axis=-1, epsilon=1e-5)(x)
    x = PReLU(alpha_initializer=initializers.constant(0.25), shared_axes=[1, 2])(x)
    return x

def bottleneck(inputs, filters, kernel, t, strides, r=False):
    tchannel = K.int_shape(inputs)[-1] * t
    x = conv_block(inputs, tchannel, 1, 1, "same")
    x = DepthwiseConv2D(kernel, strides=strides, padding="same", depth_multiplier=1, use_bias=False,
                        depthwise_initializer=initializers.random_normal(stddev=0.1),
                        bias_initializer='zeros')(x)
    x = BatchNormalization(axis=-1, epsilon=1e-5)(x)
    x = PReLU(alpha_initializer=initializers.constant(0.25), shared_axes=[1, 2])(x)
    x = Conv2D(filters, 1, strides=1, padding="same", use_bias=False,
               kernel_initializer=initializers.random_normal(stddev=0.1),
               bias_initializer='zeros')(x)
    x = BatchNormalization(axis=-1, epsilon=1e-5)(x)
    if r:
        x = add([x, inputs])
    return x


def inverted_residual_block(inputs, filters, kernel, t, n):
    x = inputs
    for _ in range(n):
        x = bottleneck(x, filters, kernel, t, 1, True)
    return x


def relu6(x):
    return K.relu(x, max_value=6)


def channel_attention(input_feature, ratio=8):
    channel = K.int_shape(input_feature)[-1]
    ratio = min(ratio, channel)
    shared_layer_one = Dense(channel // ratio,
                             activation='relu',
                             kernel_initializer='he_normal',
                             use_bias=True,
                             bias_initializer='zeros')
    shared_layer_two = Dense(channel,
                             kernel_initializer='he_normal',
                             use_bias=True,
                             bias_initializer='zeros')
    avg_pool = GlobalAveragePooling2D()(input_feature)
    avg_pool = shared_layer_one(avg_pool)
    avg_pool = shared_layer_two(avg_pool)
    max_pool = GlobalMaxPooling2D()(input_feature)
    max_pool = shared_layer_one(max_pool)
    max_pool = shared_layer_two(max_pool)
    cbam_feature = Add()([avg_pool, max_pool])
    attention_weights_channel = Activation('sigmoid')(cbam_feature)
    return Multiply()([input_feature, attention_weights_channel]), attention_weights_channel


def spatial_attention(input_feature):
    kernel_size = 7
    cbam_feature = input_feature
    avg_pool = Lambda(lambda x: K.mean(x, axis=3, keepdims=True))(cbam_feature)
    max_pool = Lambda(lambda x: K.max(x, axis=3, keepdims=True))(cbam_feature)
    concat = Concatenate(axis=3)([avg_pool, max_pool])
    cbam_feature = Conv2D(filters=1,
                          kernel_size=kernel_size,
                          strides=1,
                          padding='same',
                          activation='sigmoid',
                          kernel_initializer='he_normal',
                          use_bias=False)(concat)
    attention_weights_spatial = cbam_feature
    return Multiply()([input_feature, attention_weights_spatial]), attention_weights_spatial


def cbam_block(cbam_feature, ratio=8):
    cbam_feature, attention_weights_channel = channel_attention(cbam_feature, ratio)
    cbam_feature, attention_weights_spatial = spatial_attention(cbam_feature)
    return cbam_feature, attention_weights_channel, attention_weights_spatial


def mobilefacenet(inputs, embedding_size, dropout_keep_prob=0.5):
    input_shape = K.int_shape(inputs)
    height = input_shape[1]
    width = input_shape[2]
    y_min = 0
    y_max = height // 2
    x_min = 0
    x_max = width
    above_nose_region = Lambda(lambda img: tf.image.crop_to_bounding_box(
        img, y_min, x_min, y_max - y_min, x_max - x_min
    ))(inputs)
    above_nose_region_with_attention, _, _ = cbam_block(above_nose_region)
    def put_back_region(img, region, x_min, y_min):
        shape = K.int_shape(img)
        zeros = tf.zeros_like(img)
        region_padded = tf.image.pad_to_bounding_box(region, y_min, x_min, shape[1], shape[2])
        return img * zeros + region_padded
    inputs_with_attention = Lambda(lambda x: put_back_region(x[0], x[1], x_min, y_min))([inputs, above_nose_region_with_attention])
    x = conv_block(inputs_with_attention, 64, 3, 2, "same")  # Output Shape: (56, 56, 64)
    x = depthwise_conv_block(x, 64, 3, 1)  # (56, 56, 64)
    x = bottleneck(x, 64, 3, t=2, strides=2)
    x = inverted_residual_block(x, 64, 3, t=2, n=4)  # (28, 28, 64)
    x = bottleneck(x, 128, 3, t=4, strides=2)  # (14, 14, 128)
    x = inverted_residual_block(x, 128, 3, t=2, n=6)  # (14, 14, 128)
    x = bottleneck(x, 128, 3, t=4, strides=2)  # (14, 14, 128)
    x = inverted_residual_block(x, 128, 3, t=2, n=2)  # (7, 7, 128)
    x = Conv2D(512, 1, use_bias=False, name="conv2d",
               kernel_initializer=initializers.random_normal(stddev=0.1),
               bias_initializer='zeros')(x)
    x = BatchNormalization(epsilon=1e-5)(x)
    x = PReLU(alpha_initializer=initializers.constant(0.25), shared_axes=[1, 2])(x)
    x = DepthwiseConv2D(int(x.shape[1]), depth_multiplier=1, use_bias=False,
                        depthwise_initializer=initializers.random_normal(stddev=0.1),
                        bias_initializer='zeros')(x)
    x = BatchNormalization(epsilon=1e-5)(x)
    x = Conv2D(512, kernel_size=1, use_bias=False, name='sep',
               kernel_initializer=initializers.random_normal(stddev=0.1),
               bias_initializer='zeros')(x)
    x = BatchNormalization(name='sep_bn', epsilon=1e-5)(x)
    x = PReLU(alpha_initializer=initializers.constant(0.25), shared_axes=[1, 2])(x)
    x = BatchNormalization(name='bn2', epsilon=1e-5)(x)
    x = Dropout(p=dropout_keep_prob)(x)
    x = Flatten()(x)
    x = Dense(embedding_size, name='linear',
              kernel_initializer=initializers.random_normal(stddev=0.1),
              bias_initializer='zeros')(x)
    x = BatchNormalization(name='features', epsilon=1e-5)(x)
    return x
