from flask import Blueprint, request, jsonify
from routes.user_route import user_bp
from routes.task_route import task_bp
from config import app, db
from flask_cors import CORS
import os

CORS(app)  # Enable CORS for all routes

# Register the blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(task_bp, url_prefix='/api')


@app.route('/')
def index():
    return jsonify({'message': 'Welcome to the Task Management API!'}), 200

# allowing the server to handle serving static files 
@app.route('/assets/<path:filename>')
def serve_static(filename):
    import os
    from flask import send_from_directory
    assets_folder = os.path.join(os.getcwd(), 'assets')
    return send_from_directory(assets_folder, filename)

# run in debug mode
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=port)
