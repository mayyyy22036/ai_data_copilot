from datetime import datetime

from pydantic import BaseModel


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    tool_used: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationOut(BaseModel):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationDetail(ConversationOut):
    messages: list[MessageOut]


class MessageCreate(BaseModel):
    message: str


class MessageResponse(BaseModel):
    conversation_id: int
    answer: str
    tool_used: str
