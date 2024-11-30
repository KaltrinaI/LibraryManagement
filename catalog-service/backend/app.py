from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'catalogue_db')
DB_USER = os.getenv('DB_USER', 'mysql')
DB_PASSWORD = os.getenv('DB_PASS', '')

def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,        # Docker Compose service name for the database
        user=DB_USER,    # Matches MYSQL_USER in docker-compose.yml
        password=DB_PASSWORD, #Matches MYSQL_PASSWORD in docker-compose.yml
        database=DB_NAME      # Matches MYSQL_DATABASE in docker-compose.yml
    )

#Get all books
@app.route('/books', methods=['GET'])
def get_books():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    conn.close()
    return jsonify(books)

#Add a book
@app.route('/books', methods=['POST'])
def add_book():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO books (title, author, stock) VALUES (%s, %s, %s)",
        (data['title'], data['author'], data['stock'])
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Book added successfully'}), 201

# Delete book
@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the book exists
    cursor.execute("SELECT * FROM books WHERE id = %s", (id,))
    book = cursor.fetchone()

    if not book:
        conn.close()
        return jsonify({'error': 'Book not found'}), 404

    # Proceed to delete the book
    cursor.execute("DELETE FROM books WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Book deleted successfully'}), 200

#Update book
@app.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE books SET title = %s, author = %s, stock = %s WHERE id = %s",
        (data['title'], data['author'], data['stock'], id)
    )
    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({'error': 'Book not found'}), 404
    
    return jsonify({'message': 'Book updated successfully'})

#Get book by id
@app.route('/books/<int:id>', methods=['GET'])
def get_book_by_id(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books WHERE id = %s", (id,))
    book = cursor.fetchone()
    conn.close()

    if not book:
        return jsonify({'error': 'Book not found'}), 404

    return jsonify(book)


#Get book by author
@app.route('/books/author/<string:author>', methods=['GET'])
def get_books_by_author(author):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books WHERE author = %s", (author,))
    books = cursor.fetchall()
    conn.close()

    if not books:
        return jsonify({'error': 'No books found for this author'}), 404

    return jsonify(books)

#Get book by name
@app.route('/books/name/<string:name>', methods=['GET'])
def get_books_by_name(name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM books WHERE title LIKE %s"
    cursor.execute(query, (f"%{name}%",))  # Use LIKE for partial matches
    books = cursor.fetchall()
    conn.close()

    if not books:
        return jsonify({'error': 'No books found with this name'}), 404

    return jsonify(books)

@app.route('/books/updatestock/<int:id>', methods=['PUT'])
def update_stock(id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the book exists
    cursor.execute("SELECT * FROM books WHERE id = %s", (id,))
    book = cursor.fetchone()

    if not book:
        conn.close()
        return jsonify({'error': 'Book not found'}), 404

    # Update stock only
    if 'stock' in data:
        cursor.execute("UPDATE books SET stock = %s WHERE id = %s", (data['stock'], id))
        conn.commit()
        conn.close()

        if cursor.rowcount == 0:
            return jsonify({'error': 'Failed to update stock'}), 500

        return jsonify({'message': 'Stock updated successfully'}), 200
    else:
        conn.close()
        return jsonify({'error': 'Stock field is required'}), 400



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
