import tensorflow as tf
import tensorflow_datasets as tfds

####GLOBAL VARIABLES AND FUNCTIONS

def normalize(input_image, input_mask):
  input_image = tf.cast(input_image, tf.float32) / 255.0
  #input_mask -= 1
  return input_image, input_mask

def load_image(datapoint):
  input_image = tf.image.resize(datapoint['image'], (128, 128))
  input_mask = tf.image.resize(datapoint['segmentation_mask'], (128, 128))

  input_image, input_mask = normalize(input_image, input_mask)

  return input_image, input_mask

def create_mask(pred_mask):
  pred_mask = tf.argmax(pred_mask, axis=-1)
  pred_mask = pred_mask[..., tf.newaxis]
  return pred_mask[0]

####END GLOBAL DEFINITIONS


def show_predictions(dataset=None, num=1): 
    for image in dataset:
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

        cutout.save('cutout.png')
      
        cutout.putdata(newImageData)
      
        cutout.save('newImage.jpg')

model = tf.keras.models.load_model('ImageSegmentation/model 90-10 only background.h5')

testImages = []
testImg = tf.keras.preprocessing.image.load_img('ImageSegmentation/test 5.jpg')
testImg = tf.image.resize(testImg, [128, 128])
img_array = tf.cast(testImg, tf.float32) / 255.0
batch = tf.expand_dims(img_array, 0)
testImages.append(batch)

#show_predictions(test_batches, 1)


show_predictions(testImages, 1)