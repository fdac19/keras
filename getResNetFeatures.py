from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, GlobalAveragePooling2D
from tensorflow.keras.models import Model
import cv2, sys, os, csv, glob
import pandas as pd
import numpy as np
import pymongo
from StringIO import StringIO
from bson.binary import Binary
import json


def extract_coordinates(img_info, width, height):
    all_coor = json.loads(img_info['location'])[0]['geometry']
    x1, y1, x2, y2 = [10000, 10000, 0, 0]
    for point in all_coor['points']:
        x = int(float(point['x'] * width))
        y = int(float(point['y'] * height))
        if x <= x1:
            x1 = x
        if y <= y1:
            y1 = y
        if x >= x2:
            x2 = x
        if y >= y2:
            y2 = y
    return x1, y1, x2, y2

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
db = client ['fdac19-tags']
coll = db ['users']
#change to your netid
myNetId = 'anau'
uid = coll .find_one ({'username':myNetId})['_id'];
coll = db ['tags']

toProcess = {}
for t in coll .find ({'user':uid}):
  img = t ['image']
  tg = t ['tag']
  ids = t ['_id']
  img = img .replace ("http://localhost:3000/","public/")
  toProcess [ids] = img

img_size = 224

missed_imgs = []

for pId in toProcess .keys ():
  path = toProcess [pId]
  exists = os.path.isfile(path)
  if exists:
    sz = os.path.getsize(path)
    if (sz < 15000000L):
      print (path)
    else:
      missed_imgs.append(path)
      next
  else:
    missed_imgs.append(path)
    next

  try:
    imf = StringIO(open(path,'rb').read())
    bif = Binary(imf.getvalue())
    img_object = cv2.imread (path)
    height, width = img_object.shape[:2]

    # extract all of the information for the corresponding img
    res = coll .find_one ({'_id': pId, 'user':uid}, {"feature": 0, "imgCont": 0 } )
    # find the coordinate for the rectangle that includes the object
    x1, y1, x2, y2 = extract_coordinates(res, width, height)

    # crop out the tag area from the img
    cropped_img = img_object[y1:y2, x1:x2]
    #resize the image
    img_object = cv2.resize (cropped_img, (img_size, img_size))

    # resnet featurs for the original cropped image
    fv1 = get_featur(img_object)

    # resnet featurs for the clockwise rotated cropped image
    img_rotate_90_clockwise = cv2.rotate(img_object, cv2.ROTATE_90_CLOCKWISE)
    fv2 = get_featur(img_rotate_90_clockwise)

    # resnet featurs for the counterclockwise rotated cropped image
    img_rotate_90_counterclockwise = cv2.rotate(img_object, cv2.ROTATE_90_COUNTERCLOCKWISE)
    fv3 = get_featur(img_rotate_90_counterclockwise)


    # resnet featurs for the 180 rotated cropped image
    img_rotate_180 = cv2.rotate(img_object, cv2.ROTATE_180)
    fv4 = get_featur(img_rotate_180)

    # resnet featurs for flipped up cropped image
    img_flip_ud = cv2.flip(img_object, 0)
    fv5 = get_featur(img_flip_ud)

    # resnet featurs for flipped lr cropped image
    img_flip_lr = cv2.flip(img_object, 1)
    fv6 = get_featur(img_flip_lr)

    res2 = coll.update_one ({'_id': pId, 'user':uid}, { "$set" : {"feature": fv1,"feature2": fv2 ,"feature3": fv3, "feature4": fv4,"feature5": fv5,"feature6": fv6,"imgCont": bif} } )

  except Exception as e:
    print (e)
    missed_imgs.append(path)
