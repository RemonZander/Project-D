import os
import tensorflow as tf
import numpy as np

img_height = 180
img_width = 180

img_urls = [
    ("Jack Jones Poloshirt", "https://media.s-bol.com/3l5kj2WvkQZM/157x210.jpg"),
    ("Jack & Jones Glenn Slim Ft Heren Jeans", "https://media.s-bol.com/JZmO141NrDoD/71x210.jpg"),
    ("Teva W Dames Sandalen", "https://media.s-bol.com/xlR1l6EjjJl3/168x78.jpg"),
]

batches = [

]

class_names = [
    "broeken",
    "jassen",
    "korte broeken",
    "slippers",
    "sneakers",
    "t-shirts",
]

for index, url in enumerate(img_urls):
    path = tf.keras.utils.get_file(str(index), origin=url[1], cache_subdir="datasets/prediction_data")
    img = tf.keras.utils.load_img(path, target_size=(img_height, img_width))
    img_array = tf.keras.utils.img_to_array(img)
    batch = tf.expand_dims(img_array, 0)
    batches.append((url[0], batch))

model = tf.keras.models.load_model(os.path.abspath('./Server/NeuralNets/ImageClassifier/model.h5'))

print("==================================================Start Prediction=================================================")
for batch in batches:
    predictions = model.predict(batch[1])
    score = tf.nn.softmax(predictions[0])
    print("Image used for prediction is: " + batch[0])
    print("This image most likely belongs to {} with a {:.2f} percent confidence.".format(class_names[np.argmax(score)], 100 * np.max(score)))
print("==================================================End Prediction=================================================")