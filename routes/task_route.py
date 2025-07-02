from flask import Blueprint, request, jsonify
from models import Tasks, TaskAttachments, TaskUsers
from config import db
from datetime import datetime

task_bp = Blueprint('tasks', __name__)

@task_bp.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    new_task = Tasks(
        title=data.get('title'),
        description=data.get('description'),
        user_id=data.get('user_id'),
        priority=data.get('priority'),
        status=data.get('status'),
        due_date=datetime.strptime(data.get("due_date"), '%Y-%m-%d').date()
    )
    assigned_to = data.get('assigned_to', [])
    if assigned_to:
        for user_id in assigned_to:
            task_user = TaskUsers(
                task_id=new_task.id,
                user_id=user_id
            )
            task_user.save()

    new_task.save()
    return jsonify({'message': 'Task created successfully!'}), 201

@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Tasks.query.all()
    return jsonify([task.to_dict() for task in tasks]), 200

@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    task = Tasks.query.get_or_404(task_id)
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.user_id = data.get('user_id', task.user_id)
    task.priority = data.get('priority', task.priority)
    task.status = data.get('status', task.status)
    task.due_date = due_date=datetime.strptime(data.get("due_date"), '%Y-%m-%d').date() if data.get("due_date") else task.due_date
    task.save()


    assigned_to = data.get('assigned_to', [])  # e.g. [2, 3, 4]

    # Get existing task-user links for this task
    task_users = TaskUsers.query.filter_by(task_id=task.id).all()
    current_user_ids = {tu.user_id for tu in task_users}

    # Add new users not already assigned
    for user_id in assigned_to:
        if user_id not in current_user_ids:
            new_task_user = TaskUsers(task_id=task.id, user_id=user_id)
            db.session.add(new_task_user)

    # Remove users that are no longer assigned
    for task_user in task_users:
        if task_user.user_id not in assigned_to:
            db.session.delete(task_user)

    db.session.commit()



    return jsonify({'message': 'Task updated successfully!'}), 200

@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Tasks.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted successfully!'}), 200


#updating attachments and task_users routes
@task_bp.route('/tasks/<int:task_id>/attachments', methods=['POST'])
def add_attachment(task_id):
    data = request.get_json()
    new_attachment = TaskAttachments(
        task_id=task_id,
        file_path=data.get('file_path'),
        user_id=data.get('user_id')
    )
    new_attachment.save()
    return jsonify({'message': 'Attachment added successfully!'}), 201

@task_bp.route('/tasks/<int:task_id>/users', methods=['POST'])
def add_task_user(task_id):
    data = request.get_json()
    new_task_user = TaskUsers(
        task_id=task_id,
        user_id=data.get('user_id')
    )
    new_task_user.save()
    return jsonify({'message': 'User added to task successfully!'}), 201

@task_bp.route('/tasks/<int:task_id>/attachments', methods=['GET'])
def get_attachments(task_id):
    attachments = TaskAttachments.query.filter_by(task_id=task_id).all()
    return jsonify([attachment.to_dict() for attachment in attachments]), 200

@task_bp.route('/tasks/<int:task_id>/users', methods=['GET'])
def get_task_users(task_id):
    task_users = TaskUsers.query.filter_by(task_id=task_id).all()
    return jsonify([task_user.to_dict() for task_user in task_users]), 200

@task_bp.route('/tasks/<int:task_id>/attachments/<int:attachment_id>', methods=['DELETE'])
def delete_attachment(task_id, attachment_id):
    attachment = TaskAttachments.query.filter_by(task_id=task_id, id=attachment_id).first_or_404()
    db.session.delete(attachment)
    db.session.commit()
    return jsonify({'message': 'Attachment deleted successfully!'}), 200

@task_bp.route('/tasks/<int:task_id>/users', methods=['PUT'])
def delete_task_user(task_id):
    # bulk update, get users that we want there, remove the rest
    data = request.get_json()
    task_users = TaskUsers.query.filter_by(task_id=task_id).all()
    user_ids = {user.user_id for user in task_users}
    for user in data.get('user_ids', []):
        if user not in user_ids:
            new_task_user = TaskUsers(
                task_id=task_id,
                user_id=user
            )
            new_task_user.save()
    for task_user in task_users:
        if task_user.user_id not in data.get('user_ids', []):
            db.session.delete(task_user)
    db.session.commit()
    return jsonify({'message': 'Task users updated successfully!'}), 200
