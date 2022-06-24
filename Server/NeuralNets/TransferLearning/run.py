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

img_height = 160
img_width = 160

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

img_urls_jeans = [
    #JEANS WITH HUMANS
    #RIPPED JEANS
    ("Ripped jeans 1", "https://media.glamour.com/photos/5e542262f0fb3c00084c553c/1:1/w_2560%2Cc_limit/ripped-thigh-jeans.jpeg"),
    ("Ripped jeans 2","https://i.insider.com/5ae892c67708e976f86240bb?width=700"),

    #Regular jeans frontview
    ("Regular fit stretch jeans, straight", "https://image01.bonprix.nl/assets/460x644/1642409133/19339429-3PcU60Wk.jpg"),
    ("Jeans rechte pijpen - gescheurd", "https://images.asos-media.com/products/stradivarius-jaren-90-jeans-met-rechte-pijpen-en-scheuren-in-blauw/22006562-4?$n_640w$&wid=513&fit=constrain"),
    ("Jeans hearts", "https://cdn.shopify.com/s/files/1/0073/0438/0480/products/75758b739997ee013098610c8013f924_620x.jpg?v=1602487150"),
    #("Jeans high waist","https://i.otto.nl/i/otto/53cfd80e-a8c9-50ad-8fd2-3571f2763684/lascana-high-waist-jeans-met-modieuze-band-blauw.jpg?$ovnl_seo_index$"),
    ("Jeans pink", "https://img.ltwebstatic.com/images3_pi/2020/09/29/1601372056474d4a0740a58cb97345b95ba54a9b01.webp"),
    ("Black pants red flame", "https://img.ltwebstatic.com/images3_pi/2021/04/06/1617671831dc1ed60a49c4cfe8f059415d5e3d6cc8.webp"),
    ("red pants","https://assets.teenvogue.com/photos/5db1f67b7a4bfb00098c01ca/master/w_320%2Cc_limit/asos2.jpgimage.png"),
    #Regular jeans sideview
    ("Side view jeans", "https://www.refinery29.com/images/10308983.jpg"),
    ("Side view jeans 2", "https://cdn.shopify.com/s/files/1/0248/2205/5015/products/dutil-denim-vancouver-calgary-toronto-jude-neale-hanna-skinny-antique-womens-3_600x901.jpg?v=1646774195"),
    ("side view jeans 3", "https://media.glamour.com/photos/569592e393ef4b09520d248f/master/pass/fashion-2015-08-00-frayed-jeans-main.jpg"),
    
    #Regular jeans rearview
    ("Rearview jeans 1", "https://cdn.theatlantic.com/thumbor/UE5skrCbtCPxUggXIKtXmxc494E=/535x118:2407x1990/1080x1080/media/img/mt/2019/08/shutterstock_742819582/original.jpg"),
    ("Achterzijde witte broek", "https://www.shoeby.nl/dw/image/v2/BGFJ_PRD/on/demandware.static/-/Sites-master-catalog/default/dw27bfa636/products/1097355/05_1097355_2.jpg?sw=1200&q=100"),
    #High waisted jeans
    ("High waisted jeans", "https://onemorerep.imgix.net/18248-large_default2x/embrace-high-waist-jeans.jpg?auto=format"),
    ("many backsides","https://imagesvc.meredithcorp.io/v3/mm/image?url=https%3A%2F%2Fstatic.onecms.io%2Fwp-content%2Fuploads%2Fsites%2F23%2F2021%2F02%2F26%2Fskinny-jeans-gen-z-2000.jpg"),
    ("pants rearview zoom","https://m.media-amazon.com/images/I/51mG+V1WTpL._AC_UX569_.jpg"),

    ("Jeans Rihanna", "https://assets.vogue.com/photos/62127c140b84a2f429d4241b/master/pass/BGUS_2318213_004.jpg"),
    ("Plofbroek", "https://images.contentstack.io/v3/assets/blt5a5988820e5f83f8/bltd3a10300bed366d0/5f08de430395fe7f7bb10a9e/Header_W_Straight.jpg?disable=upscale&width=225&format=pjpg&quality=90"),
    ("High waisted jeans 2", "https://www.benetton.com/dw/image/v2/BBSF_PRD/on/demandware.static/-/Sites-ucb-master/default/dwf98f3ac2/images/Full_Card_v/Benetton_22P_4YO7DF004_901_F_Full_Card_v.jpg?sw=960&sh=1280"),
    ("Hardmode jeans","https://i.insider.com/5ae892c67708e976f86240bb?width=700"),
    ("Jeans in garage", "https://cdn.cliqueinc.com/posts/292437/best-baggy-jeans-292437-1617147944041-promo.700x0c.jpg"),

    #COLORPANTS
    ("colorful pants", "https://img01.ztat.net/article/spp-media-p1/c0e553ba3454440680f2037f50ac401f/7d02b3dc35e8484baa09bcf3906953ef.jpg?imwidth=1800"),
    ("Black pants pink", "https://img01.ztat.net/article/spp-media-p1/107f517ed4e44e76830ef419c737c239/b74ce90acda84bc3a01437e341e40b48.jpg?imwidth=1800"),
    ("Rainbow pants","https://hips.hearstapps.com/vader-prod.s3.amazonaws.com/1650473656-1175376-055-3-1650473648.jpg"),
    #JEANS SEPARATE
    ("Black jeans", "https://ae01.alicdn.com/kf/HTB1hy6bRpXXXXXuXpXXq6xXFXXXP/Sokotoo-mannen-mode-zwarte-schedel-slang-zwaard-3D-print-jeans-Casual-gekleurde-patroon-stretch-denim-broek.jpg"),
    
]
#[("Red mini pants", "https://cdn2.bigcommerce.com/server5100/eq1xm6/products/14161/images/21312/HPRedFrontm__02103.1398804869.400.559.jpg?c=2")

#]
batches = [

]

class_names = [
    "jassen",
    "lange broeken",
    "korte broeken",
    "slippers",
    "sneakers",
    "t-shirts",
]

for index, url in enumerate(img_urls_jeans):
    path = tf.keras.utils.get_file(slugify(url[0]), origin=url[1], cache_subdir="datasets/prediction_data")
    img = tf.keras.utils.load_img(path, target_size=(img_height, img_width))
    img_array = tf.keras.utils.img_to_array(img)
    batch = tf.expand_dims(img_array, 0)
    batches.append((url[0], batch))

model = tf.keras.models.load_model("TLMobileNetV2TFModel.h5")

print("==================================================Start Prediction=================================================")
total_pants_percent = 0
wrong_guesses = 0
for batch in batches:
    predictions = model.predict(batch[1])
    score = tf.nn.softmax(predictions[0])
    predicted_class = class_names[np.argmax(score)]
    if predicted_class != "broeken":
        wrong_guesses += 1

    percent_pants = round(100 * np.max(score[0]) ,2) # First index of score is pants prediction, times 100 for %, rounded to 2 decimal

    total_pants_percent += percent_pants
   # print("TOTAL PANTS" + str(total_pants_percent))
    #print("Pants: " + str(percent_pants))
    percent_amount = 100 * np.max(score)
    print("Image used for prediction is: " + batch[0])
    print("This image most likely belongs to {} with a {:.2f} percent confidence.".format(predicted_class, percent_amount))
print("==================================================End Prediction=================================================")
print(f"RESULTS: % pants: {total_pants_percent / len(img_urls_jeans)}")
print(f"GUESSED WRONG: {wrong_guesses}/{len(img_urls_jeans)} %: {wrong_guesses /len(img_urls_jeans)}")