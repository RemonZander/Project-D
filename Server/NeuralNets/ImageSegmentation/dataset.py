# coding=utf-8
# Copyright 2022 The TensorFlow Datasets Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Oxford-IIIT pet dataset."""

import os

import tensorflow as tf

import tensorflow_datasets.public_api as tfds

_DESCRIPTION = """\
fuck me
"""

_CITATION = """\
no...
"""

_LABEL_CLASSES = [
    "jassen", "korte_broeken", "lange_broeken",
    "slippers", "sneakers", "t-shirts"
]

class boldataset(tfds.core.GeneratorBasedBuilder):
  """Oxford-IIIT pet dataset."""

  VERSION = tfds.core.Version("1.0.0")

  def _info(self):
    return tfds.core.DatasetInfo(
        builder=self,
        description=_DESCRIPTION,
        features=tfds.features.FeaturesDict({
            "image":
                tfds.features.Image(),
            "label":
                tfds.features.ClassLabel(names=_LABEL_CLASSES),
            "file_name":
                tfds.features.Text(),
            "segmentation_mask":
                tfds.features.Image(shape=(None, None, 1), use_colormap=True)
        }),
        supervised_keys=("image", "label"),
        homepage="http://www.robots.ox.ac.uk/~vgg/data/pets/",
        citation=_CITATION,
    )

  def _split_generators(self, unknown):
    """Returns splits."""
    images_path_dir = "E:\\school bestanden\\HBO\\Informatica\\2020-2025\\Projecten\\Project D\\segmentation dataset\\images"
    annotations_path_dir = "E:\\school bestanden\\HBO\\Informatica\\2020-2025\\Projecten\\Project D\\segmentation dataset\\masks"

    # Setup train and test splits
    train_split = tfds.core.SplitGenerator(
        name="train",
        gen_kwargs={
            "images_dir_path":
                images_path_dir,
            "annotations_dir_path":
                annotations_path_dir,
            "images_list_file":
                os.path.join("E:\\school bestanden\\HBO\\Informatica\\2020-2025\\Projecten\\Project D\\segmentation dataset", "train.txt"),
        },
    )
    test_split = tfds.core.SplitGenerator(
        name="test",
        gen_kwargs={
            "images_dir_path": images_path_dir,
            "annotations_dir_path": annotations_path_dir,
            "images_list_file": os.path.join("E:\\school bestanden\\HBO\\Informatica\\2020-2025\\Projecten\\Project D\\segmentation dataset", "test.txt")
        },
    )

    return [train_split, test_split]

  def _generate_examples(self, images_dir_path, annotations_dir_path,
                         images_list_file):
    with tf.io.gfile.GFile(images_list_file, "r") as images_list:
      for line in images_list:
        #image_name, label = line.strip().split(" ")
        temp = line.split()
        image_name, label = temp[0], temp[1]

        #trimaps_dir_path = os.path.join(annotations_dir_path, "masks")

        trimap_name = image_name + ".jpg"
        image_name += ".jpg"
        label = int(label) - 1

        record = {
            "image": os.path.join(images_dir_path, image_name),
            "label": int(label),
            "file_name": image_name,
            "segmentation_mask": os.path.join("E:\\school bestanden\\HBO\\Informatica\\2020-2025\\Projecten\\Project D\\segmentation dataset\\masks", trimap_name)
        }
        yield image_name, record