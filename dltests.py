from __future__ import absolute_import
from __future__ import print_function

from keras.datasets import mnist
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import SGD
from keras.utils import np_utils
from keras.optimizers import RMSprop
from elephas.spark_model import SparkModel
from elephas.utils.rdd_utils import to_simple_rdd

from pyspark import SparkContext, SparkConf

# Define basic parameters
batch_size = 60
nb_classes = 10
epochs =3
#99.64 for 256 and 300

# Create Spark context
conf = SparkConf().setMaster("local").setAppName("neural")
sc = SparkContext(conf = conf)

# Load data
(x_train, y_train), (x_test, y_test) = mnist.load_data()

x_train = x_train.reshape(60000, 784)
x_test = x_test.reshape(10000, 784)
x_train = x_train.astype("float32")
x_test = x_test.astype("float32")
x_train /= 255
x_test /= 255
print(x_train.shape[0], 'train samples')
print(x_test.shape[0], 'test samples')

# Convert class vectors to binary class matrices
y_train = np_utils.to_categorical(y_train, nb_classes)
y_test = np_utils.to_categorical(y_test, nb_classes)

model = Sequential()
model.add(Dense(128, input_dim=784))

model.add(Activation('relu'))
model.add(Dropout(0.2))
model.add(Dense(128))

model.add(Activation('relu'))
model.add(Dropout(0.2))
model.add(Dense(115))

model.add(Activation('relu'))
model.add(Dropout(0.2))
model.add(Dense(75))

model.add(Activation('relu'))
model.add(Dropout(0.2))
model.add(Dense(55))

model.add(Activation('relu'))
model.add(Dropout(0.2))
model.add(Dense(30))

model.add(Activation('relu'))
model.add(Dropout(0.2))
model.add(Dense(10))


model.add(Activation('softmax'))

sgd = SGD(lr=0.1)
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# Build RDD from numpy features and labels
rdd = to_simple_rdd(sc, x_train, y_train)

# Initialize SparkModel from Keras model and Spark context
spark_model = SparkModel(model, frequency='epoch', mode='asynchronous')

# Train Spark model
spark_model.fit(rdd, epochs=epochs, batch_size=batch_size, verbose=0, validation_split=0.1)
# Evaluate Spark model by evaluating the underlying model
score = spark_model.master_network.evaluate(x_test, y_test, verbose=2)
print("\n")
print("\n")
print('Test accuracy:', score[1])
print("\n")
print("\n")
