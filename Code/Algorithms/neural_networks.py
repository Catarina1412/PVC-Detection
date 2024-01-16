import numpy as np
import tensorflow as tf
import pandas as pd
sys.path.append('./Code/preprocessing')
from extract_features import features
from sklearn.model_selection import train_test_split
import sys
sys.path.append('./Code/dataset')
from string_to_list import ecg_to_list, rpeak_to_list, pvcs_to_list
import tensorflow as tf
#from sklearn.externals import joblib
import joblib
import os

# Loading the dataset for training
data_path = os.path.abspath('./Data/dataPVC.csv')
dataset = pd.read_csv(data_path)
r, pvc = dataset['r_peaks ind'], dataset.pvc
qrs = dataset.ecg
qrs = ecg_to_list(qrs)

# Feature Extraction
ftrs = features(qrs, r)
ftrs = np.array(ftrs)

# Labels
labels = pvc

'''
# Balancing the dataset
majority_class_indices = np.where(labels == 0)[0]
remove_count = int((np.sum(labels == 0) - np.sum(labels == 1)) * 0.9)
remove_indices = np.random.choice(majority_class_indices, size=remove_count, replace=False)

balanced_features = np.delete(features, remove_indices, axis=0)
balanced_labels = np.delete(labels.values, remove_indices)
'''

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(ftrs, labels, test_size=0.2, random_state=42)

# Define neural network model
model = tf.keras.models.Sequential([
  tf.keras.layers.Dense(64, activation='relu'),
  tf.keras.layers.Dense(1, activation='sigmoid')
])

# Tensor the data
x_train_tensor = tf.convert_to_tensor((X_train))
y_train_tensor = tf.convert_to_tensor((y_train))
x_test_tensor = tf.convert_to_tensor((X_test))
y_test_tensor = tf.convert_to_tensor((y_test))

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', patience=5)

model.fit(x_train_tensor, y_train_tensor, epochs=50, batch_size=32, validation_data=(x_test_tensor, y_test_tensor), callbacks=[early_stopping])

filename = './Code/Algorithms/Neural_networks.joblib'
joblib.dump(model, filename)