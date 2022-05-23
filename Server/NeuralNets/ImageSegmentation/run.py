import tensorflow as tf

def create_mask(pred_mask):
  pred_mask = tf.argmax(pred_mask, axis=-1)
  pred_mask = pred_mask[..., tf.newaxis]
  return pred_mask[0]

def show_predictions(dataset=None, num=1): 
    for image in dataset[0:num]:
        pred_mask = model.predict(image)
        new_mask = create_mask(pred_mask)

        old_image = tf.keras.utils.array_to_img(image[0])
        cutout = tf.keras.utils.array_to_img(new_mask)
        cutout = cutout.convert("RGB")

        imgData = old_image.getdata()

        d = cutout.getdata()
        newImageData = []
        for i, pixelData in enumerate(d):
            if pixelData[0] == 127:
                newImageData.append((255, 255, 255))
            else:
                newImageData.append(imgData[i])

        cutout.save('cutout.jpg')
      
        cutout.putdata(newImageData)
      
        cutout.save('newImage.jpg')

model = tf.keras.models.load_model('ImageSegmentation/model.h5')

testImages = []
testImg = tf.keras.preprocessing.image.load_img('ImageSegmentation/test data/broeken/0-0.jpg')
img_array = tf.cast(testImg, tf.float32) / 255.0
batch = tf.expand_dims(img_array, 0)
testImages.append(batch)

show_predictions(testImages, 1)