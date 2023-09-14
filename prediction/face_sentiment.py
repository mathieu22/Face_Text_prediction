from skimage.io import imread
from skimage.transform import resize
from skimage.feature import hog
from skimage import exposure
from skimage.color import rgb2gray
import numpy as np
import joblib
import sys

def face_prediction(filename):
    sentiments = ['surprise','disgust','fear','happy','sad','angry','neutral']
    img = imread('./static/uploads/'+filename)
    if len(img.shape) == 3:
        img = rgb2gray(img)

    img = resize(img,(64,64))
    fd= hog(img, orientations=9, pixels_per_cell=(8, 8), 
                            cells_per_block=(2, 2), visualize=True)
    model = joblib.load('Model/knn.joblib')
    y = np.array(fd[0])
    y = y.reshape(1,-1)
    pred = model.predict(y)
    return sentiments[int(pred[0])-1]