"""
Usage:
Specify paths to:
    training and test sets;
    screenshots screen size;
    CSV input path and output paths.

Outputs two CSV files (training and test), with labels and positions.
These CSV files will be used to generate TFRecord format files.
"""
import pandas as pd
import os
from collections import OrderedDict

# set paths to training and test sets
training_set_path = os.path.join('.', 'training_set')
test_set_path = os.path.join('.', 'test_set')

train_fnames = os.listdir(training_set_path)
test_fnames = os.listdir(test_set_path)

# screenshots size, this could be inferred but since I took it localy I know the values
screen_width = 1366
screen_height = 768

# CSV file names
window_positions_path = 'windows_positions.csv'
training_labels_path = 'training_labels.csv'  # output fname
test_labels_path = 'test_labels.csv'  # output fname

# import window position data
windows_positions = pd.read_csv(
    window_positions_path,
    header=0)

# split to training and test labels
training_set_labels = []
test_set_labels = []

for window_ind, window_row in windows_positions.iterrows():
    row = OrderedDict()
    row['filename'] = str(window_row.observation_id) + '.png'
    row['width'] = screen_width
    row['height'] = screen_height
    row['class'] = 'Chrome'
    row['xmin'] = window_row.pos_x
    row['ymin'] = window_row.pos_y
    row['xmax'] = window_row.pos_x2
    row['ymax'] = window_row.pos_y2
    
    # test if this should go to training or testing CSV
    if row['filename'] in train_fnames:
        training_set_labels.append(row)
    elif row['filename'] in test_fnames:
        test_set_labels.append(row)
    else:
        raise ValueError('Encoutered unknown file')

# convert OrderedDict to df
training_set_labels = pd.DataFrame(training_set_labels)
test_set_labels = pd.DataFrame(test_set_labels)

# export to CSV
training_set_labels.to_csv(
    training_labels_path, 
    index=False)

test_set_labels.to_csv(
    test_labels_path, 
    index=False)

