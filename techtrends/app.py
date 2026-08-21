import sqlite3
import json
import logging
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

connection_count = 0


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global connection_count
    connection_count += 1
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                            (post_id,)).fetchone()
    connection.close()
    return post

def get_post_count():
    connection = get_db_connection()
    post_count = connection.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    connection.close()
    return post_count

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
# Set up logging: normal events to STDOUT, warnings/errors to STDERR
formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.addFilter(lambda record: record.levelno < logging.WARNING)
stdout_handler.setFormatter(formatter)

stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setLevel(logging.WARNING)
stderr_handler.setFormatter(formatter)

app.logger.handlers.clear()
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(stdout_handler)
app.logger.addHandler(stderr_handler)
app.logger.propagate = False

# Also capture Werkzeug logs (for request info), same stdout/stderr split
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.INFO)
werkzeug_logger.handlers.clear()
werkzeug_logger.addHandler(stdout_handler)
werkzeug_logger.addHandler(stderr_handler)
werkzeug_logger.propagate = False

# Define the main route of the web application
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.warning("A non-existing article is accessed.")
        return render_template('404.html'), 404
    else:
        app.logger.info(f'Article "{post["title"]}" retrieved.')
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('The "About us" page is retrieved')
    return render_template('about.html')

# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                                (title, content))
            connection.commit()
            connection.close()

            app.logger.info(f'Article "{title}" is created')

        return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/healthz')
def status():
    response = app.response_class(
        response=json.dumps({"result": "OK - healthy"}),
        status=200,
        mimetype='application/json'
    )
    app.logger.info('Health status retrieved.')
    return response

@app.route('/metrics')
def metrics():
    post_count = get_post_count()
    response = app.response_class(
        response=json.dumps({"status": "success", "code": 0, "data": {"db_connection_count": connection_count, "post_count": post_count}}),
        status=200,
        mimetype='application/json'
    )
    return response

# start the application on port 3111
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3111)