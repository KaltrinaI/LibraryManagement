from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'user_db')
DB_USER = os.getenv('DB_USER', 'mysql')
DB_PASSWORD = os.getenv('DB_PASS', '')

def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,        # Docker Compose service name for the database
        user=DB_USER,    # Matches MYSQL_USER in docker-compose.yml
        password=DB_PASSWORD, #Matches MYSQL_PASSWORD in docker-compose.yml
        database=DB_NAME      # Matches MYSQL_DATABASE in docker-compose.yml
    )

# Register a user
@app.route('/users/register', methods=['POST'])
def register_user():
    data = request.json
    hashed_password = generate_password_hash(data['password'])
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
        (data['username'], data['email'], hashed_password)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'User registered successfully'}), 201

# User login
@app.route('/users/login', methods=['POST'])
def login_user():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (data['email'],))
    user = cursor.fetchone()
    conn.close()

    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401

    # Generate a token (for demonstration, use a placeholder)
    token = "jwt-token-placeholder"
    return jsonify({'message': 'Login successful', 'token': token})

# Get user information
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify(user)

# Update user details
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()

    updates = []
    params = []
    if 'email' in data:
        updates.append("email = %s")
        params.append(data['email'])
    if 'password' in data:
        updates.append("password = %s")
        params.append(generate_password_hash(data['password']))
    params.append(id)

    query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
    cursor.execute(query, tuple(params))
    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'message': 'User updated successfully'})

# Delete user
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (id,))
    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'message': 'User deleted successfully'})

#Get all users
@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return jsonify(users)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
