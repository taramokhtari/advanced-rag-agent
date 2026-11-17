from sqlalchemy.orm import Session, joinedload

from app.database.models import Conversation, ChatMessage


class ConversationRepository:

    @staticmethod
    def create_conversation(
        db: Session,
        session_id: str,
        title: str | None = None,
    ) -> Conversation:

        conversation = Conversation(
            session_id=session_id,
            title=title,
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        return conversation

    @staticmethod
    def get_conversation(
        db: Session,
        session_id: str,
    ) -> Conversation | None:

        return (
            db.query(Conversation)
            .options(joinedload(Conversation.messages))
            .filter(Conversation.session_id == session_id)
            .first()
        )

    @staticmethod
    def add_message(
        db: Session,
        conversation_id: int,
        role: str,
        content: str,
    ) -> ChatMessage:

        if role not in {"user", "assistant", "system"}:
            raise ValueError("Invalid message role")

        message = ChatMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )

        db.add(message)
        db.commit()
        db.refresh(message)

        return message

    @staticmethod
    def get_history(
        db: Session,
        conversation_id: int,
        limit: int = 20,
    ) -> list[ChatMessage]:

        return (
            db.query(ChatMessage)
            .filter(
                ChatMessage.conversation_id == conversation_id
            )
            .order_by(ChatMessage.created_at.desc(), ChatMessage.id.desc())
            .limit(limit)
            .all()
        )[::-1]
