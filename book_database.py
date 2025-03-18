import sqlite3

def create_database():
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
    
    conn.commit()
    conn.close()
    
    print("Database created successfully!")

if __name__ == "__main__":
    create_database()