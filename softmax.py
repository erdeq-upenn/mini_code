import tensorflow as tf

batch_size = 256 
train_iter, test_iter = tf.keras.datasets.fashion_mnist.load_data(batch_size)
