# Import required libraries
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
import numpy as np
from scipy import signal
import os
import sys
sys.path.append('./Code/dataset')
sys.path.append('./Code/preprocessing')
from string_to_list import ecg_to_list, rpeak_to_list, pvcs_to_list
import joblib
from extract_features import features

# Loading the dataset for training
data_path = os.path.abspath('./Data/dataPVC350.csv')
dataset = pd.read_csv(data_path)
r, pvc = dataset['r_peaks ind'], dataset.pvc
qrs = dataset.ecg
qrs = ecg_to_list(qrs)

# Feature Extraction
ftrs = features(qrs, r)
ftrs = np.array(ftrs)

# Split data into features and target
X = ftrs
y = pvc

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create a Random Forest classifier with 100 trees
rf = RandomForestClassifier(n_estimators=100, random_state=42)

# Fit the model on the training data
rf.fit(X_train, y_train)


new_data = pd.read_csv(data_path)
new_r, new_pvc, new_ecg = new_data['r_peaks ind'], new_data.pvc, ecg_to_list(new_data.ecg)

new_ftrs = features(new_ecg[:2098], new_r[:2098])
y_pred = rf.predict(new_ftrs)
# Evaluate the performance of the model

accuracy = accuracy_score(new_pvc[:2098], y_pred)
print('Accuracy:', accuracy)


f1 = f1_score(new_pvc[:2098], y_pred)
print('F1 score:', f1)

filename = './Code/Algorithms/Random_Forest.joblib'
joblib.dump(rf, filename)