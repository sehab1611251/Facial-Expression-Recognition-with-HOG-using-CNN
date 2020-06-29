# -*- coding: utf-8 -*-
"""465 Final.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1EFHlDa7TtDsdSfguXA_ogakPgVox95OK
"""

import keras

#Reading data from google drive
!pip install -U -q PyDrive
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials

# Authenticate and create the Drive client.
auth.authenticate_user()
gauth = GoogleAuth()
gauth.credentials = GoogleCredentials.get_application_default()
drive = GoogleDrive(gauth)

df=drive.CreateFile({'id':'1Ak33IIgXvVm2Y4vQX02trRkgc9qE0J4U'}) 
df.GetContentFile('fer2013.csv')

import pandas as pd
import numpy as np
data=pd.read_csv("fer2013.csv")

keep=data['pixels'].tolist()
arr=[]
for i in keep:
  tmp=[int(j) for j in i.split(' ')]
  tmp=np.asarray(tmp).reshape(48,48)
  arr.append(tmp.astype('float32'))
 
arr=np.asarray(arr)
keepArray=arr
arr=np.expand_dims(arr,-1)

Y = pd.get_dummies(data['emotion']).to_numpy()

X_train=arr[ :28709]
y_train=Y[ :28709]
X_test=arr[28710:32298]
y_test=Y[28710:32298]
X_valid=arr[32299:35887]
y_valid=Y[32299:35887]

def Img_Augmentor(Img_Array,Y_Array,num_of_Img,num_of_aug): # Augmentation method

  if Img_Array.ndim > 3:
    Img_Array=np.add.reduce(Img_Array, 3) # if (35887, 48, 48, 1) , then (35887, 48, 48)

  from keras.preprocessing.image import ImageDataGenerator
  datagen = ImageDataGenerator(rotation_range=40,width_shift_range=0.2,height_shift_range=0.2,
                               shear_range=0.2,zoom_range=0.2,horizontal_flip=True,fill_mode='nearest')  
  
  # random index generator
  #indx_arr=[]        
  #from random import randint
  #for _ in range(num_of_Img):
	  #value = randint(0, len(Img_Array)-1)
	  #indx_arr.append(value)
  selected_img=Img_Array[indexx] # randomly selected image

  tmp=[]
  for i in selected_img:          # expanding dimension
    aaa=i.reshape((1,)+i.shape)   
    hi=np.expand_dims(aaa,1)
    tmp.append(hi.astype('float32'))
  tmp=np.asarray(tmp)            #(1000, 1, 1, 48, 48)

  agg=[] # augmented Image array
  for i in tmp:
    aug_d=datagen.flow(i)
    aug_img=[next(aug_d)[0].astype(np.float32) for i in range(num_of_aug)]
    for j in range(0,len(aug_img)):
      agg.append(aug_img[j])

  agg=np.asarray(agg) # (3000, 1, 48, 48)
  agg=np.add.reduce(agg, 1) #(3000,48,48)

  #merging augmented image with normal image
  Img_Array=np.array(Img_Array)
  augmented_image=np.array(agg)
  new_Img_Arr=np.append(Img_Array,augmented_image,axis=0)
  new_Img_Arr=np.around(new_Img_Arr, decimals=6) # 6 decimal point
  new_Img_Arr=np.expand_dims(new_Img_Arr,-1) # shape (31709, 48, 48, 1)

  ## preparing Y_train
  Y_new=Y_Array
  y_tmp=Y_Array[indexx]
  keep_y=[] # copying original Y_train to keep_y
  for i in Y_new:
    keep_y.append(i)
  for i in y_tmp: # merging original Y and augmented Y
    for j in range(0,(num_of_aug)):
      keep_y.append(i)
  new_y_Arr=np.asarray(keep_y)  

  return new_Img_Arr,new_y_Arr  # Method ends

"""**Checking Samples Corresponding unique labels**"""

X=data['emotion']

check=X.unique()
print(check)

flag=0
for i in range(0,7):
  for j in X:
    if i==j:
      flag +=1
  print("total",i,":",flag)
  flag=0

labels=X.tolist()

indexx=[]
count=0
for i in labels:
  if(i==1):
    indexx.append(count)
  count+=1

print(indexx)

my_x,my_y=Img_Augmentor(arr,Y,547,8) #method call

my_x.shape

my_y.shape

X_train=my_x[ :28709]
y_train=my_y[ :28709]
X_test=my_x[28710:32298]
y_test=my_y[28710:32298]
X_valid=my_x[32299:35887]
y_valid=my_y[32299:35887]

"""**Training with Grayscale image**"""

new_data_x=my_x[35888:40263]
new_data_y=my_y[35888:40263]

x_train_new=np.append(X_train,new_data_x,axis=0)

x_train_new.shape

y_train_new=np.append(y_train,new_data_y,axis=0)

y_train_new.shape

from keras.models import Sequential 
from keras.layers import Conv2D  
from keras.layers.normalization import BatchNormalization
from keras.regularizers import l2
from keras.layers import LeakyReLU
from keras.layers import Activation  
from keras.layers import Dropout  
from keras.layers import MaxPooling2D  
from keras.layers import Flatten  
from keras.layers import Dense  
from keras import optimizers
from keras.callbacks import ReduceLROnPlateau, EarlyStopping, TensorBoard, ModelCheckpoint
from sklearn.metrics import accuracy_score
from keras.layers.convolutional import ZeroPadding2D

model = Sequential()

model.add(Conv2D(32, kernel_size=(3,3), padding='same', input_shape=(48,48,1),activation='relu', kernel_initializer='he_uniform'))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2,2), strides=(2,2)))

model.add(Conv2D(64, kernel_size=(3,3), padding='same',activation='relu', kernel_initializer='he_uniform'))
model.add(BatchNormalization())
model.add(Conv2D(64, kernel_size=(3,3), padding='same',activation='sigmoid', kernel_initializer='glorot_normal'))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Dropout(0.4))

model.add(Conv2D(128, kernel_size=(3,3), padding='same',activation='sigmoid', kernel_initializer='glorot_uniform'))
model.add(BatchNormalization())
model.add(Conv2D(128, kernel_size=(3,3), padding='same',activation='relu', kernel_initializer='glorot_normal'))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Dropout(0.5))

model.add(Conv2D(256, kernel_size=(3, 3), padding='same',activation='sigmoid', kernel_initializer='glorot_normal'))
model.add(BatchNormalization())
model.add(Conv2D(256, kernel_size=(3, 3), padding='same',activation='relu', kernel_initializer='glorot_normal'))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Dropout(0.5))

model.add(Flatten())
model.add(Dense(256,activation='relu', kernel_initializer='he_uniform'))
model.add(Dropout(0.5))
model.add(Dense(7,activation='softmax'))

model.summary()

from keras.optimizers import SGD, Adam
from keras.optimizers import Adamax
import tensorflow as tf
from tensorflow import keras
adamax = Adamax() 
model.compile(loss='categorical_crossentropy', optimizer=adamax, metrics= ['accuracy'])

from keras.callbacks import ReduceLROnPlateau
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.9,patience=3, min_lr=0.001)

# Training the model
history=model.fit(
          np.array(x_train_new), np.array(y_train_new),
          epochs =50,
          batch_size = 64,
          validation_data=(np.array(X_valid), np.array(y_valid)),
          verbose = 1, shuffle = True,callbacks=[reduce_lr])

accuracy=model.evaluate(X_test, y_test, verbose=0)
print("Accuracy: %.2f%%" % (accuracy[1]*100))

"""**Plotting different matrices**"""

predicted=model.predict(X_test)

def plot_confusion_matrix(cm,target_names,title='Confusion matrix',cmap=None,normalize=False):
    import matplotlib.pyplot as plt
    import numpy as np
    import itertools

    accuracy = np.trace(cm) / np.sum(cm).astype('float')
    misclass = 1 - accuracy

    if cmap is None:
        cmap = plt.get_cmap('Blues')

    plt.figure(figsize=(8, 6))
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()

    if target_names is not None:
        tick_marks = np.arange(len(target_names))
        plt.xticks(tick_marks, target_names, rotation=45)
        plt.yticks(tick_marks, target_names)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]


    thresh = cm.max() / 1.5 if normalize else cm.max() / 2
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        if normalize:
            plt.text(j, i, "{:0.4f}".format(cm[i, j]),
                     horizontalalignment="center",
                     color="white" if cm[i, j] > thresh else "black")
        else:
            plt.text(j, i, "{:,}".format(cm[i, j]),
                     horizontalalignment="center",
                     color="white" if cm[i, j] > thresh else "black")


    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.show()

from sklearn.metrics import confusion_matrix
rounded_labels_Predicted=np.argmax(predicted, axis=1)
rounded_labels_y_test=np.argmax(y_test, axis=1)
cm=confusion_matrix(rounded_labels_y_test, rounded_labels_Predicted)

labels=['Angry','Disgust','Fear','Happy','Sad','Surprise','Neutral']

plot_confusion_matrix(cm,labels,title='Confusion matrix')

from sklearn import metrics
print(metrics.classification_report(rounded_labels_y_test,rounded_labels_Predicted))

print(history.history.keys())

loss_train = history.history['loss']
loss_val = history.history['val_loss']
epochs = range(1,51)
plt.plot(epochs, loss_train, 'g', label='Training loss')
plt.plot(epochs, loss_val, 'b', label='Testing loss')
plt.title('Training and Testing loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()

loss_train = history.history['accuracy']
loss_val = history.history['val_accuracy']
epochs = range(1,51)
plt.plot(epochs, loss_train, 'g', label='Training accuracy')
plt.plot(epochs, loss_val, 'b', label='Testing accuracy')
plt.title('Training and Testing accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.show()

"""**Training with HOG**"""

# importing required libraries
from skimage.transform import resize
from skimage.feature import hog
Hog_Image=[]
Hog_feature=[]
for i in my_x:
    #generating HOG features
    fd, hog_image = hog(i, orientations=9, pixels_per_cell=(4,4),cells_per_block=(1,1), visualize=True, multichannel=True) 
    Hog_feature.append(fd)
    Hog_Image.append(hog_image)

Hog_Image=np.asarray(Hog_Image)
Hog_Image.shape

Hog_Image=np.expand_dims(Hog_Image,-1)
Hog_Image.shape

import tensorflow as tf
test=Hog_Image[0]
test=tf.squeeze(test)

from skimage.io import imread, imshow
import matplotlib.pyplot as plt
fig, (ax1) = plt.subplots(1, figsize=(8, 4), sharex=True, sharey=True) 
ax1.imshow(test, cmap=plt.cm.gray) 
ax1.set_title('Hog Image')

"""**Viewing some hog image corresponding to original images.**"""

# importing required libraries
from skimage.io import imread, imshow
from skimage.transform import resize
from skimage.feature import hog
from skimage import exposure
import matplotlib.pyplot as plt
Hog_arr=[]
for x in range(0, 4):
  img = keepArray[x]    
  fd, hog_image = hog(img, orientations=9, pixels_per_cell=(4, 4), cells_per_block=(1, 1), visualize=True)
  Hog_arr.append(hog_image)
  
fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(8, 8), sharex=True, sharey=True) 
ax1.imshow(keepArray[0], cmap=plt.cm.gray)  
ax2.imshow(keepArray[1], cmap=plt.cm.gray)  
ax3.imshow(keepArray[2], cmap=plt.cm.gray) 
ax4.imshow(keepArray[3], cmap=plt.cm.gray)     
plt.show()

fig2, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(8, 8), sharex=True, sharey=True) 
ax1.imshow(Hog_arr[0], cmap=plt.cm.gray)  
ax2.imshow(Hog_arr[1], cmap=plt.cm.gray)  
ax3.imshow(Hog_arr[2], cmap=plt.cm.gray) 
ax4.imshow(Hog_arr[3], cmap=plt.cm.gray)     
plt.show()

"""**Preparing HOG data**"""

XX_train=Hog_Image[ :28709]
yy_train=my_y[ :28709]
XX_test=Hog_Image[28710:32298]
yy_test=my_y[28710:32298]
XX_valid=Hog_Image[32299:35887]
yy_valid=my_y[32299:35887]

new_hog_x=Hog_Image[35888:40263]
new_hog_y=my_y[35888:40263]

x_train_hog=np.append(XX_train,new_hog_x,axis=0)

x_train_hog.shape

y_train_hog=np.append(yy_train,new_hog_y,axis=0)

y_train_hog.shape

# Training the model
History=model.fit(
          np.array(x_train_hog), np.array(y_train_hog),
          epochs =50,
          batch_size = 64,
          validation_data=(np.array(XX_valid), np.array(yy_valid)),
          verbose = 1,
          shuffle = True,callbacks=[reduce_lr]
          )

accuracy=model.evaluate(XX_test, yy_test, verbose=0)
print("Accuracy: %.2f%%" % (accuracy[1]*100))

predicted=model.predict(XX_test)

from sklearn.metrics import confusion_matrix
rounded_labels_Predicted=np.argmax(predicted, axis=1)
rounded_labels_y_test=np.argmax(yy_test, axis=1)
cm=confusion_matrix(rounded_labels_y_test, rounded_labels_Predicted)

plot_confusion_matrix(cm,labels,title='Confusion matrix')

from sklearn import metrics
print(metrics.classification_report(rounded_labels_y_test,rounded_labels_Predicted))

loss_train = History.history['loss']
loss_val = History.history['val_loss']
epochs = range(1,51)
plt.plot(epochs, loss_train, 'g', label='Training loss')
plt.plot(epochs, loss_val, 'b', label='Testing loss')
plt.title('Training and Testing loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()

loss_train = History.history['accuracy']
loss_val = History.history['val_accuracy']
epochs = range(1,51)
plt.plot(epochs, loss_train, 'g', label='Training accuracy')
plt.plot(epochs, loss_val, 'b', label='Testing accuracy')
plt.title('Training and Testing accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.show()