from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.graph import run_agent_graph
from app.database.session import get_db
from app.schemas.conversation import (
    ConversationDetail,
    ConversationOut,
    MessageCreate,
    MessageResponse,
)
from app.services import conversation_service

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("", response_model=ConversationOut)
def create_conversation(db: Session = Depends(get_db)) -> ConversationOut:
    conversation = conversation_service.create_conversation(db)
    return conversation


@router.get("", response_model=list[ConversationOut])
def list_conversations(db: Session = Depends(get_db)) -> list[ConversationOut]:
    return conversation_service.list_conversations(db)


@router.get("/{conversation_id}", response_model=ConversationDetail)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)) -> ConversationDetail:
    conversation = conversation_service.get_conversation(db, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation introuvable")
    return conversation


@router.post("/{conversation_id}/messages", response_model=MessageResponse)
def send_message(
    conversation_id: int, request: MessageCreate, db: Session = Depends(get_db)
) -> MessageResponse:
    conversation = conversation_service.get_conversation(db, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation introuvable")

    # 1. Sauvegarde du message utilisateur
    conversation_service.add_message(db, conversation_id, role="user", content=request.message)

    # 2. Construit un contexte simple à partir des derniers échanges
    #    (mémoire "naïve" — voir limites discutées en Phase 8)
    recent = conversation_service.get_recent_messages(db, conversation_id, limit=6)
    if len(recent) > 1:
        history_text = "\n".join(f"{m.role}: {m.content}" for m in recent[:-1])
        contextualized_question = (
            f"Historique de la conversation :\n{history_text}\n\n"
            f"Nouvelle question : {request.message}"
        )
    else:
        contextualized_question = request.message

    # 3. Appelle l'agent LangGraph (Phase 7) avec ce contexte
    result = run_agent_graph(contextualized_question)
    answer = result["answer"]
    tool_used = result["evidence"][-1]["tool"] if result["evidence"] else "direct_answer"

    # 4. Sauvegarde la réponse de l'assistant
    conversation_service.add_message(
        db, conversation_id, role="assistant", content=answer, tool_used=tool_used
    )

    return MessageResponse(conversation_id=conversation_id, answer=answer, tool_used=tool_used)
