from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['bae_cream_db']
users_collection = db['users']

@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        
        # Check if username or email already exists
        if users_collection.find_one({'$or': [
            {'username': data['username']},
            {'email': data['email']}
        ]}):
            return jsonify({
                'success': False,
                'message': 'Username or email already exists'
            }), 400

        # Add timestamp to user data
        data['created_at'] = datetime.utcnow()
        
        # Insert user data into MongoDB
        result = users_collection.insert_one(data)
        
        if result.inserted_id:
            return jsonify({
                'success': True,
                'message': 'User registered successfully',
                'user_id': str(result.inserted_id)
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to register user'
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        # Find user by username
        user = users_collection.find_one({'username': username})

        if user and user['password'] == password:
            # Don't send password in response
            user_data = {
                'name': user['name'],
                'username': user['username'],
                'email': user['email'],
                'phone': user['phone'],
                'address': user['address']
            }
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': user_data
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid username or password'
            }), 401

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 