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
clustering_model = Sequential ()
clustering_model .add (ResNet50(include_top = True, pooling='ave', weights = 'imagenet'))
clustering_model .layers[0] .trainable = False
clustering_model .compile (optimizer='sgd', loss='categorical_crossentropy', metrics=['accuracy'])

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
  row = []
  try:
    imf = StringIO (open(path,'rb').read())
    bif = Binary (imf.getvalue())
    img_object = cv2.imread (path)
    img_object = cv2.resize (img_object, (img_size, img_size))
    img_object = np.array (img_object, dtype = np.float64)
    img_object = preprocess_input (np.expand_dims(img_object.copy(), axis = 0))
    resnet_feature = clustering_model.predict (img_object)
    fv = pd.Series (resnet_feature.flatten()).to_json(orient='values')
    res = coll .update_one ({'_id': pId, 'user':uid}, { "$set" : {"feature": fv, "imgCont": bif } } )
    print (path)
  except Exception as e:
    print (e)
    missed_imgs.append(path)

