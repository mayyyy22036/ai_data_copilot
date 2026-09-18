from sqlalchemy.orm import Session

from app.database.models import Conversation, Message


def create_conversation(db: Session) -> Conversation:
    conversation = Conversation()
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def list_conversations(db: Session) -> list[Conversation]:
    return db.query(Conversation).order_by(Conversation.created_at.desc()).all()


def get_conversation(db: Session, conversation_id: int) -> Conversation | None:
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()


def add_message(
    db: Session, conversation_id: int, role: str, content: str, tool_used: str | None = None
) -> Message:
    message = Message(
        conversation_id=conversation_id, role=role, content=content, tool_used=tool_used
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_recent_messages(db: Session, conversation_id: int, limit: int = 6) -> list[Message]:
    """Les `limit` derniers messages, dans l'ordre chronologique (pas anti-chronologique)."""
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.id.desc())
        .limit(limit)
        .all()
    )
    return list(reversed(messages))
