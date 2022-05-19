import os
import tensorflow as tf
import numpy as np

img_height = 180
img_width = 180

img_urls = [
    ("Regular fit stretch jeans, straight", "https://image01.bonprix.nl/assets/460x644/1642409133/19339429-3PcU60Wk.jpg"),
    ("PETROL T-SHIRT", "https://cdn.shopify.com/s/files/1/0103/3987/6928/products/aurelien_t-shirt_men_egyptian_cotton_heren_katoen_petrol_49db354a-1f9b-49f7-b22e-0491e5d95f46_600x.jpg?v=1634569755"),
    ("Nike Air Force 1 '07", "https://static.nike.com/a/images/t_PDP_864_v1/f_auto,b_rgb:f5f5f5/350e7f3a-979a-402b-9396-a8a998dd76ab/air-force-1-07-herenschoen-pXTXQ8.png"),
    ("PME Legend Falcon Navy", "https://www.fashionforless.nl/media/catalog/product/cache/ad39a5933e487132b4cc9b7a888cdc49/p/b/pbo202041-598_1.jpg"),
    ("heren teenslippers zwart", "https://www.hema.nl/dw/image/v2/BBRK_PRD/on/demandware.static/-/Sites-HEMA-master-catalog/default/dw9529b877/product/22170701_01_001_01.jpg?sw=1058&sh=1200&sm=fit"),
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

model = tf.keras.models.load_model("ImageClassifier/model.h5")

print("==================================================Start Prediction=================================================")
for batch in batches:
    predictions = model.predict(batch[1])
    score = tf.nn.softmax(predictions[0])
    print("Image used for prediction is: " + batch[0])
    print("This image most likely belongs to {} with a {:.2f} percent confidence.".format(class_names[np.argmax(score)], 100 * np.max(score)))
print("==================================================End Prediction=================================================")