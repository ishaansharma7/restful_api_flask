from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
import os
from datetime import datetime
import traceback


######################### Setup #########################


# Initialize app
app = Flask(__name__)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Database object
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Marshmallow object
marshmallow = Marshmallow(app)


######################### Model & Schema #########################


# Blog Class/Model
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(80), nullable=False)
    body = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    def __init__(self, title, body, author, pub_date=datetime.utcnow()):
        self.title = title
        self.body = body
        self.author = author
        self.pub_date = pub_date


# Blog schema
class BlogSchema(marshmallow.Schema):
    class Meta:
        fields = ('id', 'title', 'author', 'body', 'pub_date')


# Initialise schema
blog_schema = BlogSchema()
blogs_schema = BlogSchema(many=True)


######################### APIs #########################


# Create a blog
@app.route('/blog/create', methods=['POST'])
def create_blog():
    try:
        title = request.json['title']
        body = request.json['body']
        author = request.json['author']
        new_blog = Blog(title, body, author)
        db.session.add(new_blog)
        db.session.commit()
        return blog_schema.jsonify(new_blog), 201
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400


# Get all blogs
@app.route('/blog/all', methods=['GET'])
def get_all_blogs():
    all_blogs = Blog.query.all()
    result = blogs_schema.dump(all_blogs)
    return jsonify(result)


# Get single blog
@app.route('/blog/<id>', methods=['GET'])
def get_blog(id):
    blog = Blog.query.get(id)
    if blog == None:
        return jsonify({'error': f'no blog found with the id {id}'}), 404
    return blog_schema.jsonify(blog)


# Search blog using title
@app.route('/blog/search/title/<title>', methods=['GET'])
def search_title(title):
    blog = Blog.query.filter(Blog.title.contains(title)).first()
    if blog == None:
        return jsonify({'error': f'no blog found with the title {title}'}), 404
    return blog_schema.jsonify(blog)


# Update a blog
@app.route('/blog/<id>', methods=['PUT'])
def update_blog(id):
    try:
        title = request.json['title']
        body = request.json['body']
        author = request.json['author']
        blog = Blog.query.get(id)
        blog.title = title
        blog.body = body
        blog.author = author
        db.session.commit()
        return blog_schema.jsonify(blog)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400


# Delete blog
@app.route('/blog/delete/<id>', methods=['DELETE'])
def delete_blog(id):
    blog = Blog.query.get(id)
    if blog == None:
        return jsonify({'error': f'no blog found with id {id}'}), 404
    db.session.delete(blog)
    db.session.commit()
    return blog_schema.jsonify(blog)



if __name__ == '__main__':
    app.run(debug=True, port=5000)