import numpy as np
from numpy.lib.stride_tricks import as_strided


def pool2d(a, kernel_size, stride, padding, pool_mode='max'):
    """
    2D Pooling

    Parameters:
        a: input 4D array
            a.shape = (D,H,W,C)
        kernel_size: int, the size of the window
        stride: int, the stride of the window
        padding: int, implicit zero paddings on both sides of the input
        pool_mode: string, 'max' or 'avg'
    """
    # Padding
    a = np.pad(a, padding, mode='constant')

    # Window view of a
    output_shape = (
        a.shape[0],
        (a.shape[1] - kernel_size) // stride + 1,
        (a.shape[2] - kernel_size) // stride + 1,
        a.shape[3]
    )

    kernel_size = (kernel_size, kernel_size)
    a_w = as_strided(a,
                     shape=output_shape + kernel_size,
                     strides=(a.strides[0], stride * a.strides[1], stride * a.strides[2], a.strides[3]) + a.strides[1:3]
                     )
    a_w = a_w.reshape(-1, *kernel_size)

    # Return the result of pooling
    if pool_mode == 'max':
        return a_w.max(axis=(1, 2)).reshape(output_shape)
    elif pool_mode == 'avg':
        return a_w.mean(axis=(1, 2)).reshape(output_shape)



######################################################################
# test : predictions & run_time
######################################################################
if __name__ == "__main__":
    import os
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # to ignore warning errors
    import time
    import tensorflow.keras.backend as keras
    import tensorflow.keras.layers as layers

    A = np.random.randn(3, 200, 200, 32)
    avg_time = [0, 0]
    outs = [[], []]
    x = keras.constant(A)
    pool2d_keras = layers.MaxPooling2D(pool_size=(2, 2), strides=None, padding="same", input_shape=x.shape)

    n_simulations = 10
    for _ in range(n_simulations):
        # Keras
        t1 = time.time()
        o1 = pool2d_keras(x)
        avg_time[0] += (time.time() - t1)/n_simulations
        o1 = o1.numpy()
        outs[0].append(o1)

        # our methods
        t1 = time.time()
        o2 = pool2d(A, kernel_size=2, stride=2, padding=0, pool_mode='max')
        avg_time[1] += (time.time() - t1)/n_simulations
        outs[1].append(o2)

    print("difference of predictions ", [(o1 - o2).sum() for o1, o2 in zip(*outs)])
    print("the average run time of keras: ", avg_time[0], "the average run time  of our implementation: ", avg_time[1])
    print('Ratio speed: (our_implementation/keras)', avg_time[1] / avg_time[0])


#################################################
# result
#################################################
# difference of predictions  [2.0189942075574525e-05, 2.0189942075574525e-05, 2.0189942075574525e-05, 2.0189942075574525e-05, 2.0189942075574525e-05, 2.0189942075574525e-05, 2.0189942075574525e-05, 2.0189942075574525e-05, 2.0189942075574525e-05, 2.0189942075574525e-05]
# the average run time of keras:  0.0027794837951660156 the average run time  of our implementation:  0.055673837661743164
# Ratio speed: (our_implementation/keras) 20.030279636301252
