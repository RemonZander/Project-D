import os
import tensorflow as tf
import numpy as np
import unicodedata
import re
import matplotlib.pyplot as plt

def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

img_height = 180
img_width = 180

img_urls = [
    ("Regular fit stretch jeans, straight", "https://image01.bonprix.nl/assets/460x644/1642409133/19339429-3PcU60Wk.jpg"),
    ("PETROL T-SHIRT", "https://cdn.shopify.com/s/files/1/0103/3987/6928/products/aurelien_t-shirt_men_egyptian_cotton_heren_katoen_petrol_49db354a-1f9b-49f7-b22e-0491e5d95f46_600x.jpg?v=1634569755"),
    ("Nike Air Force 1 '07", "https://static.nike.com/a/images/t_PDP_864_v1/f_auto,b_rgb:f5f5f5/350e7f3a-979a-402b-9396-a8a998dd76ab/air-force-1-07-herenschoen-pXTXQ8.png"),
    ("PME Legend Falcon Navy", "https://www.fashionforless.nl/media/catalog/product/cache/ad39a5933e487132b4cc9b7a888cdc49/p/b/pbo202041-598_1.jpg"),
    ("heren teenslippers zwart", "https://www.hema.nl/dw/image/v2/BBRK_PRD/on/demandware.static/-/Sites-HEMA-master-catalog/default/dw9529b877/product/22170701_01_001_01.jpg?sw=1058&sh=1200&sm=fit"),
    ("Chino short heren – Navy – W303", "https://www.italian-style.nl/wp-content/uploads/2021/06/eng_pl_Mens-casual-shorts-W303-blue-19533_4.jpg"),
    ("REPEAT cashmere | Jassen - Dames", "https://www.repeatcashmere.com/media/catalog/product/8/0/800154_1434-1.jpg?width=900&height=1200&canvas=900,1200&quality=80&bg-color=255,255,255&fit=bounds"),
    ("Engelse stijl wax en tweed jassen - De Blokeend", "https://www.blokeend.nl/images/fadeheaders/img_12_1572611076.jpg"),
    ("Yellow T-Shirt", "https://assets.myntassets.com/dpr_1.5,q_60,w_400,c_limit,fl_progressive/assets/images/1700944/2022/3/2/093bc645-d461-4128-94a1-0692803944141646215571321-HRX-by-Hrithik-Roshan-Men-Yellow-Printed-Cotton-Pure-Cotton--1.jpg"),
    ("White T-Shirt", "https://assets.vogue.com/photos/617c1cc0842b6d00d5ee6b61/master/w_1280%2Cc_limit/slide_13.jpg"),
    ("Magic Mike Cosplay", "https://www.partykleding.nl/image/cache/catalog/producten/2019/GH/new/lava,%20tshirt,%20clubear,%20gregg,%20homme,%20front-800x800.jpeg"),
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
    path = tf.keras.utils.get_file(slugify(url[0]), origin=url[1], cache_subdir="datasets/prediction_data")
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