import pymongo
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, GlobalAveragePooling2D
import numpy as np
from tensorflow.keras.models import Model
import cv2
import sys
import csv
import glob


imgs_path = "."

img_size = 224
resnet_weigth_path = './resnet50_weights_tf_dim_ordering_tf_kernels_notop.h5'

clustering_model = Sequential()
clustering_model.add(ResNet50(include_top = False, pooling='ave', weights = resnet_weigth_path))
clustering_model.layers[0].trainable = False


clustering_model.compile(optimizer='sgd', loss='categorical_crossentropy', metrics=['accuracy'])

missed_imgs = []

f.
for path in glob.glob(imgs_path + '/*.jpg'):
    correct_path = path
    row = []
    try:
        img_object = cv2.imread(correct_path)
        img_object = cv2.resize(img_object, (img_size, img_size))
        img_object = np.array(img_object, dtype = np.float64)
        img_object = preprocess_input(np.expand_dims(img_object.copy(), axis = 0))

        resnet_feature = clustering_model.predict(img_object)
        resnet_feature = np.array(resnet_feature)
        row.append(correct_path)
        row.extend(list(resnet_feature.flatten()))
        print(row)
    except: 
        missed_imgs.append(path)
