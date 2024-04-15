from flask import Flask, request, jsonify
from joblib import load
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pandas as pd
import secrets

app = Flask(__name__)
data, identified = '', ''
api_keys = {}
model = load('model_spam_classfication.joblib')
tfidf_vectorizer = load('tfidf_vectorizer.joblib')

# Function to generate a random API key
def generate_api_key():
    return secrets.token_hex(16)

# Function to confirm user with their API key
def confirm_user(api_key):
    return api_keys.get(api_key)

@app.route('/predict', methods=['POST'])
def predict():
    # Get API key from the request headers
    api_key = request.headers.get('x-api-key')
    
    # Check if the API key is valid
    user_id = confirm_user(api_key)
    if not user_id:
        return jsonify({'error': 'Invalid API key'}), 401
    
    # Get message from the request form data
    message = request.form.get('message')
    if not message:
        return jsonify({'error': 'Message not provided'}), 400
    
    # Vectorize the message
    message_vectorized = tfidf_vectorizer.transform([message])
    
    # Make prediction
    prediction = model.predict(message_vectorized)
    result = 'Spam' if prediction[0] == 1 else 'Not Spam'
    
    # Save predicted data
    data, identified = message, result
    df = {'User_ID': [user_id], 'Category': [identified], 'Message': [data]}
    pd.DataFrame(df).to_csv('Predicted_data.csv', mode='a', index=False, header=False)
    
    return jsonify({'message': message, 'result': result}), 200

@app.route('/register', methods=['POST'])
def register():
    # Generate API key
    api_key = generate_api_key()
    
    # Get user ID from the request data
    user_id = request.form.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID not provided'}), 400
    
    # Save the API key
    api_keys[api_key] = user_id
    
    return jsonify({'user_id': user_id, 'api_key': api_key}), 201

if __name__ == '__main__':
    app.run(debug=True)
