#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect
import shortuuid
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Create a SQLite database to store short links and analytics
conn = sqlite3.connect('url_shortener.db')
conn.execute('''
    CREATE TABLE IF NOT EXISTS urls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        long_url TEXT NOT NULL,
        short_url TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten():
    long_url = request.form['long_url']
    short_url = shortuuid.uuid()[:8]  # Generate a short URL using shortuuid

    # Save the URL in the database
    conn = sqlite3.connect('url_shortener.db')
    conn.execute('INSERT INTO urls (long_url, short_url) VALUES (?, ?)', (long_url, short_url))
    conn.commit()
    conn.close()

    return render_template('shortened.html', short_url=short_url)

@app.route('/<short_url>')
def redirect_to_long_url(short_url):
    # Retrieve the long URL from the database
    conn = sqlite3.connect('url_shortener.db')
    result = conn.execute('SELECT long_url FROM urls WHERE short_url = ?', (short_url,)).fetchone()
    conn.close()

    if result:
        long_url = result[0]
        # Log analytics data
        log_analytics(short_url)
        return redirect(long_url)
    else:
        return "Short URL not found", 404

def log_analytics(short_url):
    # Log analytics data (you can enhance this based on your requirements)
    conn = sqlite3.connect('url_shortener.db')
    conn.execute('UPDATE urls SET analytics = analytics + 1 WHERE short_url = ?', (short_url,))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    app.run(debug=True)
