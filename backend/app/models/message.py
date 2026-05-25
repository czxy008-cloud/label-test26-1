from datetime import datetime
from ..extensions import db


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    receiver_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship("User", foreign_keys=[sender_id],
                             backref=db.backref("sent_messages", lazy="dynamic"))
    receiver = db.relationship("User", foreign_keys=[receiver_id],
                               backref=db.backref("received_messages", lazy="dynamic"))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "content": self.content,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
