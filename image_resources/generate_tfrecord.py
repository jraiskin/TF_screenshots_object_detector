"""
Usage:
    # Based on the following, from tensorflow/models/ github repo:
    https://github.com/tensorflow/models/blob/master/object_detection/g3doc/using_your_own_dataset.md
    
    # Example:
    python generate_tfrecord.py --csv_input=$PATH_TO/labels.csv  --image_dir=$PATH_TO_IMAGES  --output_path=$PATH_TO/labels.record

    # Create train data:
    python generate_tfrecord.py --csv_input=training_labels.csv --image_dir=training_set  --output_path=train.record

    # Create test data:
    python generate_tfrecord.py --csv_input=test_labels.csv --image_dir=test_set  --output_path=test.record
"""
from __future__ import division, print_function

import os
import io
import pandas as pd
import tensorflow as tf

import sys
# Add the object_detection folder path to the sys.path list
sys.path.append('..')

from PIL import Image
from object_detection.utils import dataset_util

flags = tf.app.flags
flags.DEFINE_string('csv_input', '', 'Path to the CSV input')
flags.DEFINE_string('output_path', '', 'Path to output TFRecord')
flags.DEFINE_string('image_dir', '', 'Path to images')
FLAGS = flags.FLAGS


def class_text_to_int(row_label):
    if row_label == 'Chrome':
        return 1
    else:
        None


def create_tf_example(row):
    full_path = os.path.join(os.getcwd(), 
                             FLAGS.image_dir, 
                             '{}'.format(row['filename']))
    with tf.gfile.GFile(full_path, 'rb') as fid:
        encoded_png = fid.read()
    encoded_png_io = io.BytesIO(encoded_png)
    image = Image.open(encoded_png_io)
    width, height = image.size

    filename = row['filename'].encode('utf8')
    image_format = b'png'
    xmins = [row['xmin'] / width]
    xmaxs = [row['xmax'] / width]
    ymins = [row['ymin'] / height]
    ymaxs = [row['ymax'] / height]
    classes_text = [row['class'].encode('utf8')]
    classes = [class_text_to_int(row['class'])]

    tf_example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': dataset_util.int64_feature(height),
        'image/width': dataset_util.int64_feature(width),
        'image/filename': dataset_util.bytes_feature(filename),
        'image/source_id': dataset_util.bytes_feature(filename),
        'image/encoded': dataset_util.bytes_feature(encoded_png),
        'image/format': dataset_util.bytes_feature(image_format),
        'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
        'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
        'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
        'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
        'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
        'image/object/class/label': dataset_util.int64_list_feature(classes),
    }))
    return tf_example


def main(_):
    writer = tf.python_io.TFRecordWriter(FLAGS.output_path)
    examples = pd.read_csv(FLAGS.csv_input)
    for index, row in examples.iterrows():
        tf_example = create_tf_example(row)
        writer.write(tf_example.SerializeToString())

    writer.close()


if __name__ == '__main__':
    tf.app.run()
