from email.mime import image
from pickle import NONE, TRUE
import tensorflow as tf
import tensorflow_datasets as tfds
from tensorflow_examples.models.pix2pix import pix2pix
from IPython.display import clear_output
import matplotlib.pyplot as plt
from PIL import Image

####GLOBAL VARIABLES AND FUNCTIONS
dataset, info = tfds.load('oxford_iiit_pet:3.*.*', with_info=True)
TRAIN_LENGTH = info.splits['train'].num_examples
BATCH_SIZE = 64
BUFFER_SIZE = 1000
STEPS_PER_EPOCH = TRAIN_LENGTH // BATCH_SIZE
model = "";

def normalize(input_image, input_mask):
  input_image = tf.cast(input_image, tf.float32) / 255.0
  input_mask -= 1
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

def show_predictions(dataset=None, num=1):
    #for image, mask in dataset.take(num):    
    #for image in dataset[0:num]:
        image = dataset[0]
        #pred_mask = model((NONE, image), training=False)
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

train_images = dataset['train'].map(load_image, num_parallel_calls=tf.data.AUTOTUNE)
test_images = dataset['test'].map(load_image, num_parallel_calls=tf.data.AUTOTUNE)
test_batches = test_images.batch(BATCH_SIZE)

####END GLOBAL DEFINITIONS

class Augment(tf.keras.layers.Layer):
  def __init__(self, seed=42):
    super().__init__()
    # both use the same seed, so they'll make the same random changes.
    self.augment_inputs = tf.keras.layers.RandomFlip(mode="horizontal", seed=seed)
    self.augment_labels = tf.keras.layers.RandomFlip(mode="horizontal", seed=seed)

  def call(self, inputs, labels):
    inputs = self.augment_inputs(inputs)
    labels = self.augment_labels(labels)
    return inputs, labels

class trainModel():
    base_model = tf.keras.applications.MobileNetV2(input_shape=[128, 128, 3], include_top=False)
    base_model_outputs = ""
    train_batches = ""
    down_stack = ""
    model = "";
    OUTPUT_CLASSES = 3
    EPOCHS = 20
    VAL_SUBSPLITS = 5
    model_history = ""
    VALIDATION_STEPS = info.splits['test'].num_examples//BATCH_SIZE//VAL_SUBSPLITS

    # Use the activations of these layers
    layer_names = [
    'block_1_expand_relu',   # 64x64
    'block_3_expand_relu',   # 32x32
    'block_6_expand_relu',   # 16x16
    'block_13_expand_relu',  # 8x8
    'block_16_project',      # 4x4
    ]

    up_stack = [
    pix2pix.upsample(512, 3),  # 4x4 -> 8x8
    pix2pix.upsample(256, 3),  # 8x8 -> 16x16
    pix2pix.upsample(128, 3),  # 16x16 -> 32x32
    pix2pix.upsample(64, 3),   # 32x32 -> 64x64
    ]

    def __init__(self):
        self.train_batches = (
            train_images
            .cache()
            .shuffle(BUFFER_SIZE)
            .batch(BATCH_SIZE)
            .repeat()
            .map(Augment())
            .prefetch(buffer_size=tf.data.AUTOTUNE))
        self.base_model_outputs = [self.base_model.get_layer(name).output for name in self.layer_names]
        # Create the feature extraction model
        self.down_stack = tf.keras.Model(inputs=self.base_model.input, outputs=self.base_model_outputs)
        self.down_stack.trainable = False

        self.model = self.unet_model(output_channels=self.OUTPUT_CLASSES)
        self.model.compile(optimizer='adam',
                      loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                      metrics=['accuracy'])
        tf.keras.utils.plot_model(self.model, show_shapes=True)
        

    def TrainModel(self):
        self.model_history = self.model.fit(self.train_batches, epochs=self.EPOCHS,
                            steps_per_epoch=STEPS_PER_EPOCH,
                            validation_steps=self.VALIDATION_STEPS,
                            validation_data=test_batches)

        self.model.save('ImageSegmentation/model.h5')

        return self.model

    def unet_model(self, output_channels:int):
        inputs = tf.keras.layers.Input(shape=[128, 128, 3])

        # Downsampling through the model
        skips = self.down_stack(inputs)
        x = skips[-1]
        skips = reversed(skips[:-1])

        # Upsampling and establishing the skip connections
        for up, skip in zip(self.up_stack, skips):
            x = up(x)
            concat = tf.keras.layers.Concatenate()
            x = concat([x, skip])

        # This is the last layer of the model
        last = tf.keras.layers.Conv2DTranspose(
            filters=output_channels, kernel_size=3, strides=2,
            padding='same')  #64x64 -> 128x128

        x = last(x)

        return tf.keras.Model(inputs=inputs, outputs=x)

#trainModelClass = trainModel()

#model = trainModelClass.TrainModel()

model = tf.keras.models.load_model('ImageSegmentation/model.h5')

#show_predictions(test_batches, 1)

testImages = []
testImg = tf.keras.preprocessing.image.load_img('ImageSegmentation/test data/broeken/0-0.jpg')

testImg2 = tf.image.resize(testImg, [128, 128])
testImg2 = tf.cast(testImg2, tf.float32) / 255.0
testImages.append(testImg2)

show_predictions(testImages, 1)