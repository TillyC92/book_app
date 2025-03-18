# setup.py
import os
import sqlite3

def init_database():
    # Create database
    conn = sqlite3.connect('bookshelf.db')
    cursor = conn.cursor()
    
    # Create Books table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        isbn TEXT,
        publication_year INTEGER,
        publisher TEXT,
        genre TEXT,
        page_count INTEGER,
        description TEXT,
        cover_url TEXT,
        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create Reading Status table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reading_status (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER NOT NULL,
        status TEXT NOT NULL,
        rating INTEGER,
        start_date DATE,
        finish_date DATE,
        notes TEXT,
        FOREIGN KEY (book_id) REFERENCES books (id)
    )
    ''')
    
    # Create static folders if they don't exist
    if not os.path.exists('static'):
        os.makedirs('static')
    if not os.path.exists('static/css'):
        os.makedirs('static/css')
    if not os.path.exists('static/js'):
        os.makedirs('static/js')
    
    # Create empty CSS file
    with open('static/css/style.css', 'w') as f:
        f.write('/* Custom styles can be added here */')
    
    # Create empty JS file
    with open('static/js/script.js', 'w') as f:
        f.write('// Custom JavaScript can be added here')
    
    # Create templates folder if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Add some sample data
    sample_books = [
        ('To Kill a Mockingbird', 'Harper Lee', '9780061120084', 1960, 'HarperCollins', 'Fiction', 281, 
         'The unforgettable novel of a childhood in a sleepy Southern town and the crisis of conscience that rocked it.', 
         'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1553383690i/2657.jpg'),
        ('1984', 'George Orwell', '9780451524935', 1949, 'Signet Classics', 'Dystopian', 328,
         'Among the seminal texts of the 20th century, Nineteen Eighty-Four is a rare work that grows more haunting as its futuristic purgatory becomes more real.',
         'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1657781256i/61439040.jpg'),
        ('The Great Gatsby', 'F. Scott Fitzgerald', '9780743273565', 1925, 'Scribner', 'Classics', 180,
         'The story of the fabulously wealthy Jay Gatsby and his love for the beautiful Daisy Buchanan.',
         'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1490528560i/4671.jpg')
    ]
    
    for book in sample_books:
        cursor.execute('''
            INSERT INTO books (title, author, isbn, publication_year, publisher, genre, page_count, description, cover_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', book)
        
        # Get the book_id to add sample reading status
        book_id = cursor.lastrowid
        
        # Add sample reading status (randomly distributed)
        if book_id % 3 == 0:
            status = 'Read'
            rating = 5
        elif book_id % 3 == 1:
            status = 'Currently Reading'
            rating = None
        else:
            status = 'Want to Read'
            rating = None
            
        cursor.execute('''
            INSERT INTO reading_status (book_id, status, rating)
            VALUES (?, ?, ?)
        ''', (book_id, status, rating))
    
    conn.commit()
    conn.close()
    
    print("Database initialized with sample data!")
    print("Run 'python app.py' to start the application")

if __name__ == "__main__":
    init_database()