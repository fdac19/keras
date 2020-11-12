from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, GlobalAveragePooling2D
from tensorflow.keras.models import Model
import cv2, sys, os, csv, glob
import pandas as pd
import numpy as np
import pymongo
from io  import StringIO
from bson.binary import Binary
import json
from bson.objectid import ObjectId


def get_featur(img):
    clustering_model = Sequential ()
    clustering_model .add (ResNet50(include_top = False, pooling='ave', weights = 'imagenet'))
    clustering_model .add (GlobalAveragePooling2D()) # get from 7x7x2048 to 2048
    clustering_model .layers[0] .trainable = False
    clustering_model .compile (optimizer='sgd', loss='categorical_crossentropy', metrics=['accuracy'])

    img_object_array = np.array (img, dtype = np.float64)
    img_object_array = preprocess_input (np.expand_dims(img_object_array.copy(), axis = 0))
    resnet_feature = clustering_model.predict(img_object_array)
    fv = pd.Series(resnet_feature.flatten()).to_json(orient='values')
    return fv

client = pymongo.MongoClient () # the gcp instance forwards back to da1
db = client ['fdac20-tags']
coll = db ['tags']


img_size = 224

missed_imgs = []


path = sys .argv[1]
uid = sys .argv[2]
cl1 = sys .argv[3]
cl2 = sys .argv[4]


try:
  #imf = StringIO(open(path,'rb').read())
  #bif = Binary(imf.getvalue())
  img_object = cv2.imread (path)
  img_object = cv2.resize(img_object, (img_size, img_size))
  #height, width = img_object.shape[:2]
  print ("here")

  # find the coordinate for the rectangle that includes the object
  #x1, y1, x2, y2 = extract_coordinates(img_object, width, height)

  # resnet featurs for the original cropped image
  print ("fv0") 
  fv1 = get_featur(img_object)
  print ("fv1") 
  # resnet featurs for the clockwise rotated cropped image
  img_rotate_90_clockwise = cv2.rotate(img_object, cv2.ROTATE_90_CLOCKWISE)
  fv2 = get_featur(img_rotate_90_clockwise)

  print ("fv2")
  # resnet featurs for the counterclockwise rotated cropped image
  img_rotate_90_counterclockwise = cv2.rotate(img_object, cv2.ROTATE_90_COUNTERCLOCKWISE)
  fv3 = get_featur(img_rotate_90_counterclockwise)
   
  print ("fv3")
  # resnet featurs for the 180 rotated cropped image
  img_rotate_180 = cv2.rotate(img_object, cv2.ROTATE_180)
  fv4 = get_featur(img_rotate_180)

  print ("fv4")
  # resnet featurs for flipped up cropped image
  img_flip_ud = cv2.flip(img_object, 0)
  fv5 = get_featur(img_flip_ud)

  print ("fv5")
  # resnet featurs for flipped lr cropped image
  img_flip_lr = cv2.flip(img_object, 1)
  fv6 = get_featur(img_flip_lr)
  
  res2 = coll.insert_one ({'path':path, 'cl1':cl1, 'cl2':cl2, 'user':uid, "feature": fv1,"feature2": fv2 ,"feature3": fv3, "feature4": fv4,"feature5": fv5,"feature6": fv6 } )

  print (path)
except Exception as e:
  print (e)
  missed_imgs.append(path)
