from flask import Blueprint, request, jsonify, current_app
from models import User
from config import db
import bcrypt
import os
from werkzeug.utils import secure_filename
from PIL import Image
from datetime import datetime

user_bp = Blueprint('users', __name__)

ASSETS_FOLDER = os.path.join(os.getcwd(), 'assets')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file):
    if not allowed_file(file.filename):
        return None
    filename = secure_filename(f"{datetime.utcnow().timestamp()}_{file.filename}")
    filepath = os.path.join(ASSETS_FOLDER, filename)
    img = Image.open(file)
    img.save(filepath)
    return f"/assets/{filename}"

@user_bp.route('/users', methods=['POST'])
def create_user():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    image_file = request.files.get('image')

    if not all([name, email, password]):
        return jsonify({'error': 'Missing required fields'}), 400

    image_url = "/assets/default.jpg"
    if image_file:
        image_url = save_image(image_file)

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    new_user = User(
        name=name,
        email=email,
        password=hashed_password,
        image=image_url
    )
    new_user.save()
    return jsonify({'message': 'User created successfully!'}), 201

@user_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    image_file = request.files.get('image')

    if name:
        user.name = name
    if email:
        user.email = email
    if password:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user.password = hashed_password

    if image_file:
        # Delete old image if it's not default
        if user.image and user.image != "/assets/default.jpg":
            try:
                os.remove(os.path.join(os.getcwd(), user.image.strip("/")))
            except FileNotFoundError:
                pass
        # Save new image
        user.image = save_image(image_file)

    user.save()
    return jsonify({'message': 'User updated successfully!'}), 200

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):   
    user = User.query.get_or_404(user_id)

    # Delete profile image if not default
    if user.image and user.image != "/assets/default.jpg":
        try:
            os.remove(os.path.join(os.getcwd(), user.image.strip("/")))
        except FileNotFoundError:
            pass

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully!'}), 200
