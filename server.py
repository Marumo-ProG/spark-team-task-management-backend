from flask import Blueprint, request, jsonify
from routes.user_route import user_bp
from routes.task_route import task_bp
from config import app, db

# Register the blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(task_bp, url_prefix='/api')

@app.route('/')
def index():
    return jsonify({'message': 'Welcome to the Task Management API!'}), 200

# run in debug mode
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Database initialized and tables created.")
    app.run(debug=True)
