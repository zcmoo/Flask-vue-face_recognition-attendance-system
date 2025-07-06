import tensorflow as tf
from keras import backend as K
from keras import initializers
from keras.layers import (BatchNormalization, Conv2D, DepthwiseConv2D, PReLU, Flatten,
                          add, Activation, GlobalAveragePooling2D, GlobalMaxPooling2D, Multiply, Concatenate, Lambda, Reshape, Add, Dense, Dropout)


def _conv_block(inputs, filters, kernel=(3, 3), strides=(1, 1)):
    x = Conv2D(filters, kernel,
               padding='same',
               use_bias=False,
               strides=strides,
               name='conv1',
               kernel_initializer=initializers.random_normal(stddev=0.1),
               bias_initializer='zeros')(inputs)
    x = BatchNormalization(name='conv1_bn', epsilon=1e-5)(x)
    return Activation(relu6, name='conv1_relu')(x)


def _depthwise_conv_block(inputs, pointwise_conv_filters,
                          depth_multiplier=1, strides=(1, 1), block_id=1):
    x = DepthwiseConv2D((3, 3),
                        padding='same',
                        depth_multiplier=depth_multiplier,
                        strides=strides,
                        use_bias=False,
                        name='conv_dw_%d' % block_id,
                        depthwise_initializer=initializers.random_normal(stddev=0.1),
                        bias_initializer='zeros')(inputs)

    x = BatchNormalization(name='conv_dw_%d_bn' % block_id, epsilon=1e-5)(x)
    x = Activation(relu6, name='conv_dw_%d_relu' % block_id)(x)

    x = Conv2D(pointwise_conv_filters, (1, 1),
               padding='same',
               use_bias=False,
               strides=(1, 1),
               name='conv_pw_%d' % block_id,
               kernel_initializer=initializers.random_normal(stddev=0.1),
               bias_initializer='zeros')(x)
    x = BatchNormalization(name='conv_pw_%d_bn' % block_id, epsilon=1e-5)(x)
    return Activation(relu6, name='conv_pw_%d_relu' % block_id)(x)


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


def relu6(x):
    return K.relu(x, max_value=6)

def MobilenetV1(inputs, embedding_size, dropout_keep_prob=0.5, depth_multiplier=1):
    input_shape = K.int_shape(inputs)
    height = input_shape[1]
    width = input_shape[2]
    y_min = height // 4
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
    x = _conv_block(inputs_with_attention, 32, strides=(1, 1))
    x = _depthwise_conv_block(x, 64, depth_multiplier, block_id=1)

    x = _depthwise_conv_block(x, 128, depth_multiplier, strides=(2, 2), block_id=2)
    x = _depthwise_conv_block(x, 128, depth_multiplier, block_id=3)

    x = _depthwise_conv_block(x, 256, depth_multiplier, strides=(2, 2), block_id=4)
    x = _depthwise_conv_block(x, 256, depth_multiplier, block_id=5)

    x = _depthwise_conv_block(x, 512, depth_multiplier, strides=(2, 2), block_id=6)
    x = _depthwise_conv_block(x, 512, depth_multiplier, block_id=7)
    x = _depthwise_conv_block(x, 512, depth_multiplier, block_id=8)
    x = _depthwise_conv_block(x, 512, depth_multiplier, block_id=9)
    x = _depthwise_conv_block(x, 512, depth_multiplier, block_id=10)
    x = _depthwise_conv_block(x, 512, depth_multiplier, block_id=11)

    x = _depthwise_conv_block(x, 1024, depth_multiplier, strides=(2, 2), block_id=12)
    x = _depthwise_conv_block(x, 1024, depth_multiplier, block_id=13)

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
