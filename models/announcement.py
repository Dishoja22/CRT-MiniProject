from models.db import db
from datetime import datetime

class Announcement(db.Model):
    __tablename__ = 'announcements'
    
    announcement_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __repr__(self):
        return f"<Announcement {self.title}>"
