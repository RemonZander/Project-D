import tensorflow as tf
import tensorflow_datasets as tfds

import matplotlib.pyplot as plt
import numpy as np
import os

base_model = tf.keras.models.load_model('ICmodel.h5')
base_model.summary()
model = tf.keras.models.Sequential()

#COPY BASE MODEL EXCEPT LAST LAYER (OUTPUT LAYER)
for layer in base_model.layers[0:-1]:
  model.add(layer)
model.summary()

#FREEZE MODEL
model.trainable = False

#ADD NEW LAST LAYER (2 OUTPUTS FOR CAT/DOG), ADD NAME TO AVOID ERROR
model.add(tf.keras.layers.Dense(2, name = "dense_last"))

_URL = 'https://storage.googleapis.com/mledu-datasets/cats_and_dogs_filtered.zip'
path_to_zip = tf.keras.utils.get_file('cats_and_dogs.zip', origin=_URL, extract=True)
PATH = os.path.join(os.path.dirname(path_to_zip), 'cats_and_dogs_filtered')

train_dir = os.path.join(PATH, 'train')
validation_dir = os.path.join(PATH, 'validation')

BATCH_SIZE = 32
IMG_SIZE = (180, 180)

train_dataset = tf.keras.utils.image_dataset_from_directory(train_dir,
                                                            shuffle=True,
                                                            batch_size=BATCH_SIZE,
                                                            image_size=IMG_SIZE)

validation_dataset = tf.keras.utils.image_dataset_from_directory(validation_dir,
                                                                 shuffle=True,
                                                                 batch_size=BATCH_SIZE,
                                                                 image_size=IMG_SIZE)

class_names = train_dataset.class_names

##plt.figure(figsize=(10, 10))
#for images, labels in train_dataset.take(1):
  #for i in range(9):
   # ax = plt.subplot(3, 3, i + 1)
   # plt.imshow(images[i].numpy().astype("uint8"))
   # plt.title(class_names[labels[i]])
  #  plt.axis("off")
#plt.show()

#CREATE A TEST SET FROM ORIGINAL VALIDATION DATASET
val_batches = tf.data.experimental.cardinality(validation_dataset)
test_dataset = validation_dataset.take(val_batches // 5)
validation_dataset = validation_dataset.skip(val_batches // 5)

AUTOTUNE = tf.data.AUTOTUNE

train_dataset = train_dataset.prefetch(buffer_size=AUTOTUNE)
validation_dataset = validation_dataset.prefetch(buffer_size=AUTOTUNE)
test_dataset = test_dataset.prefetch(buffer_size=AUTOTUNE)

data_augmentation = tf.keras.Sequential([
  tf.keras.layers.RandomFlip('horizontal', input_shape=(180, 180, 3)),
  tf.keras.layers.RandomRotation(0.2),
])

for image, _ in train_dataset.take(1):
  plt.figure(figsize=(10, 10))
  first_image = image[0]
  for i in range(9):
    ax = plt.subplot(3, 3, i + 1)
    augmented_image = data_augmentation(tf.expand_dims(first_image, 0))
    plt.imshow(augmented_image[0] / 255)
    plt.axis('off')
    plt.show()

#image_batch, label_batch = next(iter(train_dataset))
##feature_batch = base_model(image_batch)
#print(feature_batch.shape)

#global_average_layer = tf.keras.layers.GlobalAveragePooling2D()
#feature_batch_average = global_average_layer(feature_batch)
#print(feature_batch_average.shape)

#https://www.tensorflow.org/tutorials/images/transfer_learning
#https://youtu.be/8cN0PiZQl18