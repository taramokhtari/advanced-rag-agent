import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.connection import Base
from app.services.conversation_repo import ConversationRepository


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_create_conversation(db):
    conversation = ConversationRepository.create_conversation(
        db,
        session_id="test-session",
        title="Test conversation",
    )

    assert conversation.id is not None
    assert conversation.session_id == "test-session"
    assert conversation.title == "Test conversation"


def test_add_and_get_messages(db):
    conversation = ConversationRepository.create_conversation(
        db,
        session_id="message-session",
    )

    ConversationRepository.add_message(
        db, conversation.id, "user", "سلام"
    )
    ConversationRepository.add_message(
        db, conversation.id, "assistant", "سلام! چطور می‌توانم کمک کنم؟"
    )

    history = ConversationRepository.get_history(
        db,
        conversation.id,
    )

    assert len(history) == 2
    assert history[0].role == "user"
    assert history[0].content == "سلام"
    assert history[1].role == "assistant"


def test_get_history_preserves_chronological_order(db):
    conversation = ConversationRepository.create_conversation(
        db,
        session_id="order-session",
    )

    for i in range(5):
        ConversationRepository.add_message(
            db,
            conversation.id,
            "user",
            f"message-{i}",
        )

    history = ConversationRepository.get_history(
        db,
        conversation.id,
    )

    assert [message.content for message in history] == [
        f"message-{i}" for i in range(5)
    ]


def test_get_history_respects_limit(db):
    conversation = ConversationRepository.create_conversation(
        db,
        session_id="limit-session",
    )

    for i in range(5):
        ConversationRepository.add_message(
            db,
            conversation.id,
            "user",
            f"message-{i}",
        )

    history = ConversationRepository.get_history(
        db,
        conversation.id,
        limit=3,
    )

    assert len(history) == 3
    assert [message.content for message in history] == [
        "message-2",
        "message-3",
        "message-4",
    ]


def test_add_message_rejects_invalid_role(db):
    conversation = ConversationRepository.create_conversation(
        db,
        session_id="invalid-role-session",
    )

    with pytest.raises(ValueError, match="Invalid message role"):
        ConversationRepository.add_message(
            db,
            conversation.id,
            "invalid",
            "test",
        )
