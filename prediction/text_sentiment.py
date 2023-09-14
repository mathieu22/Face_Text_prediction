import pickle
import re
import emoji
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import tensorflow as tf
import sys


stop_words = stopwords.words("english")

def preprocess_text(text):
    # Supprimer les mentions
    text = re.sub(r'@\w+', '', text)
    
    # Supprimer les hashtags
    text = re.sub(r'#\w+', '', text)
    
    # Supprimer les liens
    text = re.sub(r'http\S+', '', text)
    
    # Remplacer les emojis par des chaînes de caractères
    text = emoji.demojize(text)
    
    # Supprimer les caractères spéciaux et les nombres
    text = re.sub(r'[^a-zA-Z ]', '', text)
    
    # Convertir en minuscules
    text = text.lower()
    
    text = word_tokenize(text)
    
    text = [word for word in text if not word in stop_words]
    
    text = " ".join(word for word in text)
    
    return text

def text_prediction(text):
    with open('Model/tokenizer.pkl', 'rb') as f:
        tk = pickle.load(f)
    model = tf.keras.models.load_model("Model/Tfidf_text_analysis/")
    predict_text = tk.texts_to_matrix([text])
    pred = model.predict(predict_text, verbose=0)
    print(pred[0][0])
    if pred[0][0] > 0.50:
        return "Positif"
    else:
        return "negative"
