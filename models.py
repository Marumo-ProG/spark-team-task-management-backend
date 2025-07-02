from config import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    image = db.Column(db.String(200), nullable=True, default='default.jpg')
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'image': self.image,
            'date_created': self.date_created.isoformat(),
            'date_updated': self.date_updated.isoformat()
        }
    def save(self):
        db.session.add(self)
        db.session.commit()
    

class Tasks(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # author = db.relationship('User', backref=db.backref('tasks', lazy=True))
    priority = db.Column(db.String(50), nullable=True, default='low')
    status = db.Column(db.String(50), nullable=True, default='todo')
    due_date = db.Column(db.Date, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'date_created': self.date_created.isoformat(),
            'date_updated': self.date_updated.isoformat(),
            'author': User.query.get(self.user_id).to_dict() if self.user_id else None,
            'priority': self.priority,
            'status': self.status,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'attachments': [attachment.to_dict() for attachment in self.attachments] if hasattr(self, 'attachments') else [],
            'assigned_to': [tu.to_dict()["user_id"] for tu in TaskUsers.query.filter_by(task_id=self.id).all()]
        }

    def save(self):
        db.session.add(self)
        db.session.commit()


class TaskAttachments(db.Model):
    __tablename__ = 'task_attachments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # task = db.relationship('Tasks', backref=db.backref('attachments', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'file_path': self.file_path,
            'date_created': self.date_created.isoformat(),
            'user_id': User.query.get(self.user_id).to_dict() if self.user_id else None
        }

    def save(self):
        db.session.add(self)
        db.session.commit()


class TaskUsers(db.Model):
    __tablename__ = 'task_users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'user_id': User.query.get(self.user_id).to_dict() if self.user_id else None,
            'date_created': self.date_created.isoformat()
        }

    def save(self):
        db.session.add(self)
        db.session.commit()