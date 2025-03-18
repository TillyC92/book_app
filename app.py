# app.py - Main Flask application
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for flash messages

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect('bookshelf.db')
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

# Routes
@app.route('/')
def index():
    conn = get_db_connection()
    
    # Get all books with their reading status
    books = conn.execute('''
        SELECT b.*, rs.status, rs.rating
        FROM books b
        LEFT JOIN reading_status rs ON b.id = rs.book_id
        ORDER BY b.date_added DESC
    ''').fetchall()
    
    conn.close()
    return render_template('index.html', books=books)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        # Get form data
        title = request.form['title']
        author = request.form['author']
        isbn = request.form.get('isbn', '')
        publication_year = request.form.get('publication_year', None)
        publisher = request.form.get('publisher', '')
        genre = request.form.get('genre', '')
        page_count = request.form.get('page_count', None)
        description = request.form.get('description', '')
        cover_url = request.form.get('cover_url', '')
        
        # Validate required fields
        if not title or not author:
            flash('Title and author are required!')
            return render_template('add_book.html')
        
        # Convert empty strings to None for numeric fields
        if publication_year == '':
            publication_year = None
        if page_count == '':
            page_count = None
            
        conn = get_db_connection()
        
        # Insert book
        cursor = conn.execute('''
            INSERT INTO books (title, author, isbn, publication_year, publisher, genre, page_count, description, cover_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, author, isbn, publication_year, publisher, genre, page_count, description, cover_url))
        
        # Get the book_id to add reading status
        book_id = cursor.lastrowid
        
        # Get reading status data
        status = request.form.get('status', 'Want to Read')
        rating = request.form.get('rating', None)
        
        # Convert empty strings to None
        if rating == '':
            rating = None
            
        # Add start/finish dates based on status
        start_date = None
        finish_date = None
        
        if status == 'Currently Reading':
            start_date = datetime.now().strftime('%Y-%m-%d')
        elif status == 'Read':
            finish_date = datetime.now().strftime('%Y-%m-%d')
        
        # Insert reading status
        conn.execute('''
            INSERT INTO reading_status (book_id, status, rating, start_date, finish_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (book_id, status, rating, start_date, finish_date))
        
        conn.commit()
        conn.close()
        
        flash('Book added successfully!')
        return redirect(url_for('index'))
        
    return render_template('add_book.html')

@app.route('/book/<int:book_id>')
def book_details(book_id):
    conn = get_db_connection()
    
    # Get book and its reading status
    book = conn.execute('''
        SELECT b.*, rs.status, rs.rating, rs.start_date, rs.finish_date, rs.notes
        FROM books b
        LEFT JOIN reading_status rs ON b.id = rs.book_id
        WHERE b.id = ?
    ''', (book_id,)).fetchone()
    
    conn.close()
    
    if book is None:
        flash('Book not found!')
        return redirect(url_for('index'))
        
    return render_template('book_details.html', book=book)

@app.route('/update_status/<int:book_id>', methods=['GET', 'POST'])
def update_status(book_id):
    conn = get_db_connection()
    
    # First check if the book exists
    book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
    
    if book is None:
        conn.close()
        flash('Book not found!')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Get form data
        status = request.form['status']
        rating = request.form.get('rating', None)
        notes = request.form.get('notes', '')
        
        # Convert empty strings to None
        if rating == '':
            rating = None
            
        # Get existing status
        existing_status = conn.execute(
            'SELECT * FROM reading_status WHERE book_id = ?', 
            (book_id,)
        ).fetchone()
        
        # Update start/finish dates based on status change
        start_date = None
        finish_date = None
        
        if existing_status:
            start_date = existing_status['start_date']
            finish_date = existing_status['finish_date']
            
            # Update dates based on new status
            if status == 'Currently Reading' and not start_date:
                start_date = datetime.now().strftime('%Y-%m-%d')
            elif status == 'Read' and not finish_date:
                finish_date = datetime.now().strftime('%Y-%m-%d')
        else:
            # No existing status, set dates based on new status
            if status == 'Currently Reading':
                start_date = datetime.now().strftime('%Y-%m-%d')
            elif status == 'Read':
                finish_date = datetime.now().strftime('%Y-%m-%d')
        
        # Update or insert reading status
        if existing_status:
            conn.execute('''
                UPDATE reading_status
                SET status = ?, rating = ?, start_date = ?, finish_date = ?, notes = ?
                WHERE book_id = ?
            ''', (status, rating, start_date, finish_date, notes, book_id))
        else:
            conn.execute('''
                INSERT INTO reading_status (book_id, status, rating, start_date, finish_date, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (book_id, status, rating, start_date, finish_date, notes))
        
        conn.commit()
        conn.close()
        
        flash('Reading status updated!')
        return redirect(url_for('book_details', book_id=book_id))
    
    # Get current reading status for the form
    reading_status = conn.execute(
        'SELECT * FROM reading_status WHERE book_id = ?', 
        (book_id,)
    ).fetchone()
    
    conn.close()
    
    return render_template('update_status.html', book=book, reading_status=reading_status)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    
    if not query:
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    
    # Search in title, author, description
    books = conn.execute('''
        SELECT b.*, rs.status, rs.rating
        FROM books b
        LEFT JOIN reading_status rs ON b.id = rs.book_id
        WHERE b.title LIKE ? OR b.author LIKE ? OR b.description LIKE ?
        ORDER BY b.date_added DESC
    ''', (f'%{query}%', f'%{query}%', f'%{query}%')).fetchall()
    
    conn.close()
    
    return render_template('search_results.html', books=books, query=query)

@app.route('/filter', methods=['GET'])
def filter_books():
    status = request.args.get('status', '')
    genre = request.args.get('genre', '')
    
    conn = get_db_connection()
    
    # Build query based on filters
    query = '''
        SELECT b.*, rs.status, rs.rating
        FROM books b
        LEFT JOIN reading_status rs ON b.id = rs.book_id
        WHERE 1=1
    '''
    params = []
    
    if status:
        query += ' AND rs.status = ?'
        params.append(status)
        
    if genre:
        query += ' AND b.genre = ?'
        params.append(genre)
        
    query += ' ORDER BY b.date_added DESC'
    
    books = conn.execute(query, params).fetchall()
    
    # Get all genres for the filter dropdown
    genres = conn.execute('SELECT DISTINCT genre FROM books WHERE genre != ""').fetchall()
    
    conn.close()
    
    return render_template('filtered_books.html', books=books, status=status, genre=genre, genres=genres)

@app.template_filter('star_rating')
def star_rating(value):
    if value is None:
        return "Not rated"
    return "★" * int(value) + "☆" * (5 - int(value))

if __name__ == '__main__':
    app.run(debug=True)