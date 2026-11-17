from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agent.agent import beauty_agent
from app.database.connection import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.conversation_repo import ConversationRepository

router = APIRouter(prefix="/api", tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    repo = ConversationRepository

    try:
        session_id = request.session_id or str(uuid4())

        conversation = repo.get_conversation(
            db,
            session_id=session_id,
        )

        if conversation is None:
            conversation = repo.create_conversation(
                db,
                session_id=session_id,
            )

        repo.add_message(
            db,
            conversation.id,
            "user",
            request.message,
        )

        history = repo.get_history(
            db,
            conversation.id,
            limit=20,
        )

        answer = await beauty_agent.chat(
            db=db,
            user_message=request.message,
            conversation_history=[
                {
                    "role": message.role,
                    "content": message.content,
                }
                for message in history[:-1]
                if message.role in {"user", "assistant"}
            ],
        )

        repo.add_message(
            db,
            conversation.id,
            "assistant",
            answer,
        )

        return ChatResponse(
            response=answer,
            session_id=session_id,
        )

    except Exception as exc:
        db.rollback()
        print(f"Chat endpoint error: {exc}")

        raise HTTPException(
            status_code=502,
            detail="ارتباط با دستیار هوشمند با مشکل مواجه شد.",
        )
