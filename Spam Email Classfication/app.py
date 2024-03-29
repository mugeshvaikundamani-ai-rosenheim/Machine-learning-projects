from flask import Flask, request, render_template
from joblib import load
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pandas as pd

app = Flask(__name__)
data,identified='',''
# Load the model and TF-IDF vectorizer
model = load('model_spam_classfication.joblib')
tfidf_vectorizer = load('tfidf_vectorizer.joblib')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    message = request.form['message']
    # Vectorize the input message
    message_vectorized = tfidf_vectorizer.transform([message])
    # Make prediction
    prediction = model.predict(message_vectorized)
    print(prediction)
    if prediction[0] == 0:
        result = 'Not Spam'
    else:
        result = 'Spam'
    data,identified=message,result
    df = {'Category': [identified], 'Message': [data]}
    pd.DataFrame(df).to_csv('Predicted_data.csv', mode='a', index=False, header=False)
    return render_template('result.html', message=message, result=result)
    
    




if __name__ == '__main__':
    app.run(debug=True)
