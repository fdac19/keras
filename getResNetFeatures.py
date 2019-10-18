import pymongo
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, GlobalAveragePooling2D
from tensorflow.keras.models import Model
import cv2
import sys
import csv
import glob
import pandas as pd
import numpy as np


client = pymongo.MongoClient () # the gcp instance forwards back to da1
db = client ['fdac19-tags']
coll = db ['users']
#change to your netid
myNetId = 'anau'
id = coll .find_one ({'username':myNetId})['_id'];
coll = db ['tags']

toProcess = {}
for t in coll .find ({'user':id}): 
  img = t ['image']
  tg = t ['tag']
  img = img .replace ("http://localhost:3000/","public/")
  toProcess [img] = tg

img_size = 224
resnet_weigth_path = './resnet50_weights_tf_dim_ordering_tf_kernels_notop.h5'
clustering_model = Sequential ()
clustering_model .add (ResNet50(include_top = False, pooling='ave', weights = resnet_weigth_path))
clustering_model .layers[0] .trainable = False
clustering_model .compile (optimizer='sgd', loss='categorical_crossentropy', metrics=['accuracy'])

missed_imgs = []
    
for path in toProcess .keys ():
  exists = os.path.isfile(path)
  if exists: print (path)
  row = []
  try:
    img_object = cv2.imread (path)
    img_object = cv2.resize (img_object, (img_size, img_size))
    img_object = np.array (img_object, dtype = np.float64)
    img_object = preprocess_input (np.expand_dims(img_object.copy(), axis = 0))

    resnet_feature = clustering_model.predict (img_object)
    print (np.array(resnet_feature).shape)
    print (np.array(resnet_feature))
    sys.exit()
    resnet_feature = pd.Series (resnet_feature).to_json(orient='values')
    #ff = json.dumps (resnet_feature, default=json_util.default)
    print (resnet_feature[1])
    #row.append (correct_path)
    #row.extend (list(resnet_feature.flatten()))
    #print (row)
  except Exception as e:
    print (e)
    missed_imgs.append(path)

