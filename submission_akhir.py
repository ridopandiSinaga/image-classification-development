# -*- coding: utf-8 -*-
"""Submission akhir.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Ifep3G5l3zkNyA6ctoW_tHb_Nmt_7uwM

#Ridopandi Sinaga

## **Data Preparation**
### Import Library
"""

# Commented out IPython magic to ensure Python compatibility.
import os, zipfile, shutil, PIL
import numpy as np
import tensorflow as tf

from tensorflow import keras
from google.colab import files

from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense
from tensorflow.keras.utils import plot_model
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import RMSprop

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
# %matplotlib inline

"""### Menginstall Kaggle"""

!pip install -q kaggle

"""### Upload Kredensial (Token API)"""

uploaded = files.upload()

"""### Konfigurasi untuk menerima datasets dari Kaggle"""

!chmod 600 /content/kaggle.json

"""### Download Dataset

kaggle datasets download -d iarunava/cell-images-for-detecting-malaria
"""

! KAGGLE_CONFIG_DIR=/content/ kaggle datasets download -d viratkothari/animal10

"""### Mengekstrak Dataset"""

local_zip = '/content/animal10.zip'
zip_ref = zipfile.ZipFile(local_zip, 'r')
zip_ref.extractall('/content')
zip_ref.close()

"""### Mendeklarasikan Direktori Dasar"""

BASE_DIR = '/content/Animals-10/'

"""### Membuat fungsi list_files untuk mengidentifikasi jumlah file"""

def list_files(startpath):
  num_files = 0
  for root, dirs, files in os.walk(startpath):
    level = root.replace(startpath, '').count(os.sep)
    indent = ' ' * 2 * (level)
    num_files += len(files)
    print('{}{}/ {}'.format(indent, os.path.basename(root), (str(len(files)) + ' images' if len(files) > 0 else '')))

  return num_files

"""### Memanggil fungsi list_files dengan parameter variabel direktori dasar yang telah dibuat sebelumnya"""

list_files(BASE_DIR)

"""### Membuat fungsi read_files untuk membaca setiap files"""

def read_files(startpath):
  image_files = []
  for dirname, dirnames, filenames in os.walk(startpath):
    for filename in filenames:
      image_files.append(os.path.join(dirname, filename))

  return image_files

"""### Menghapus file yang tidak digunakan"""

ignore_dir = ['sheep', 'cow', 'butterfly', 'horse', 'elephant', 'cat', 'squirrel']

for dir in ignore_dir:
  path = os.path.join(BASE_DIR, dir)
  shutil.rmtree(path)

print(os.listdir(BASE_DIR))

"""### Memastikan ukuran image yang beragam dengan fungsi PIL"""

full_dirs = read_files(BASE_DIR)
image_sizes = []
for file in full_dirs:
  image = PIL.Image.open(file)
  width, height = image.size
  image_sizes.append(f'{width}x{height}')

unique_sizes = set(image_sizes)

print(f'Size all images: {len(image_sizes)}')
print(f'Size unique images: {len(unique_sizes)}')
print(f'First 10 unique images: \n{list(unique_sizes)[:10]}')

"""Terdapat 27558 gambar dan 1627 diantaranya memiliki ukuran yang beragam

## **Data Preprocessing dan Data Splitting**

### Melakukan Augmentasi Gambar
"""

train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    horizontal_flip=True,
    shear_range = 0.2,
    zoom_range = 0.2,
    fill_mode = 'nearest',
    validation_split = 0.2)

"""## Data Image Generator"""

train_generator = train_datagen.flow_from_directory(
    BASE_DIR,
    target_size=(150, 150),
    batch_size=128,
    class_mode='categorical',
    subset='training')

validation_generator = train_datagen.flow_from_directory(
    BASE_DIR,
    target_size=(150, 150),
    batch_size=128,
    class_mode='categorical',
    subset='validation')

"""## Modelling and compile it"""

#modelling
model = Sequential()

model.add(Conv2D(32, (3,3), activation='relu', input_shape=(150, 150, 3))),
model.add(MaxPooling2D(2, 2)),

model.add(Conv2D(64, (3,3), activation='relu')),
model.add(MaxPooling2D(2,2)),

model.add(Conv2D(128, (3,3), activation='relu')),
model.add(MaxPooling2D(2,2)),

model.add(Conv2D(128, (3,3), activation='relu')),
model.add(MaxPooling2D(2,2)),

model.add(Flatten()),

model.add(Dense(512, activation='relu')),
model.add(Dense(3, activation='softmax')),

model.summary()

# compiling model
model.compile(optimizer=tf.optimizers.Adam(),
              loss='categorical_crossentropy',
              metrics = ['accuracy'])

"""## Training model"""

#callback function to stop training

class Callback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('accuracy') and logs.get('val_accuracy') > 0.90):
      print("\n Horray, data training  accuracy has been rate  above 90%")
      self.model.stop_training = True

callbacks = Callback()


# Training model
history = model.fit(
    train_generator,
    epochs=50,
    validation_data=validation_generator,
    verbose=2,
    callbacks=[callbacks])

"""## **Plot Accuracy & Loss**"""

loss = result.history['loss']
val_loss = result.history['val_loss']
acc = result.history['accuracy']
val_acc = result.history['val_accuracy']

plt.figure(figsize=(15, 5))

plt.subplot(1, 2, 1)
plt.title('Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.plot(loss, label='Training set')
plt.plot(val_loss, label='Validation set', linestyle='--')
plt.legend()
plt.grid(linestyle='--', linewidth=1, alpha=0.5)

plt.subplot(1, 2, 2)
plt.title('Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.plot(acc, label='Training set')
plt.plot(val_acc, label='Validation set', linestyle='--')
plt.legend()
plt.grid(linestyle='--', linewidth=1, alpha=0.5)

plt.show()

print(train_generator.class_indices)

uploaded = files.upload()

# Predicting images
for up in uploaded.keys():
    path = up
    img  = image.load_img(path, target_size = (150, 150))

    imgplot = plt.imshow(img)
    x       = image.img_to_array(img)
    x       = np.expand_dims(x, axis = 0)

    images  = np.vstack([x])
    classes = model.predict(images, batch_size = 10)
    print(up)

    predicted_class = np.argmax(classes)

    if predicted_class == 0:
      print('Chicken')
    elif predicted_class == 1:
      print('Dog')
    elif predicted_class == 2:
      print('Spider')
    else:
      print('Unclassified')

"""## **Convert to TFLite**"""

converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

with tf.io.gfile.GFile('model__v1.tflite', 'wb') as f:
  f.write(tflite_model)