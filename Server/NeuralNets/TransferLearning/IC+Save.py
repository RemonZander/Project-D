import matplotlib.pyplot as plt
import numpy as np
import os
import PIL
import tensorflow as tf

from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential

import pathlib

batch_size = 32
img_height = 180
img_width = 180

dataset_url = "https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz"
data_dir = tf.keras.utils.get_file('flower_photos', origin=dataset_url, untar=True)
data_dir = pathlib.Path(data_dir)

img_urls = [
    ("Sunflower", "https://h2.commercev3.net/cdn.gurneys.com/images/800/70530.jpg"),
    ("Tullip", "https://bollenstreek.nl/wp-content/uploads/2021/02/2019_04_29_019345-scaled.jpg"),
    ("Dandelion", "https://media-cldnry.s-nbcnews.com/image/upload/t_nbcnews-fp-1024-512,f_auto,q_auto:best/MSNBC/Components/Photo/_new/090915-tech-dandelion-hmed.jpg"),
    ("Daisy", "https://sakataornamentals.eu/wp-content/uploads/2020/07/Cape-Daisy-Zanzibar.jpg"),
    ("Daisy Mario", "https://static.wikia.nocookie.net/marionl/images/4/4f/DaisyMP8.gif/revision/latest?cb=20100630071809&path-prefix=nl"),
    ("Roses", "https://www.reneveyrat.fr/629-large_default2x/roses-by-the-unit-royale.jpg"),
    ("Roses with people", "https://www.hortipoint.nl/wp-content/uploads/2021/09/trosroos3-1024x677.png"),
    ("Sunflower", "https://st.focusedcollection.com/14026668/i/650/focused_268330552-stock-photo-young-woman-walking-sunflower-green.jpg"),
    ("Tullip with woman back", "https://thegorgeguide.com/staging/wp-content/uploads/2020/06/Oregon-Tulip-Festival-Tamara.jpg"),
    ("Sunflower in field", "https://www.thespruce.com/thmb/xjipBd0Qz03yxMtyOjj4CaUNqhU=/3236x2158/filters:fill(auto,1)/flower-garden-ideas-4174111-hero-12fd6f26724f45f38bc22f007ed6ada7.jpg"),
]

batches = []

for index, url in enumerate(img_urls):
    path = tf.keras.utils.get_file(str(index), origin=url[1], cache_subdir="datasets/prediction_data")
    img = tf.keras.utils.load_img(path, target_size=(img_height, img_width))
    img_array = tf.keras.utils.img_to_array(img)
    batch = tf.expand_dims(img_array, 0)
    batches.append((url[0], batch))

train_ds = tf.keras.utils.image_dataset_from_directory(
  data_dir,
  validation_split=0.2,
  subset="training",
  seed=123,
  image_size=(img_height, img_width),
  batch_size=batch_size
)

val_ds = tf.keras.utils.image_dataset_from_directory(
  data_dir,
  validation_split=0.2,
  subset="validation",
  seed=123,
  image_size=(img_height, img_width),
  batch_size=batch_size
)

class_names = train_ds.class_names

AUTOTUNE = tf.data.AUTOTUNE

train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

normalization_layer = layers.Rescaling(1./255)

normalized_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
image_batch, labels_batch = next(iter(normalized_ds))

num_classes = len(class_names)

data_augmentation = keras.Sequential(
  [
    layers.RandomFlip("horizontal", input_shape=(img_height, img_width, 3)),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.1),
  ]
)

model = Sequential([
  data_augmentation,
  layers.Rescaling(1./255),
  layers.Conv2D(16, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Conv2D(32, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Conv2D(64, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Dropout(0.2),
  layers.Flatten(),
  layers.Dense(128, activation='relu'),
  layers.Dense(num_classes)
])

model.compile(optimizer='adam', loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True), metrics=['accuracy'])

model.summary()

epochs=20
history = model.fit(train_ds, validation_data=val_ds, epochs=epochs)

print("==================================================Start Prediction=================================================")
for batch in batches:
    predictions = model.predict(batch[1])
    score = tf.nn.softmax(predictions[0])
    print("Image used for prediction is: " + batch[0])
    print("This image most likely belongs to {} with a {:.2f} percent confidence.".format(class_names[np.argmax(score)], 100 * np.max(score)))
print("==================================================End Prediction=================================================")

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']

epochs_range = range(epochs)

plt.figure(figsize=(8, 8))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.plot(epochs_range, val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()


model.save('ICmodel.h5')