# ============================================================================

from uuid import uuid4, UUID
from datetime import datetime
from app.models.user import User  # Use real model for testing
from app.models.base import BaseModel


def test_base_model_id_generation():
    """Test UUID can be set for new models"""
    user_id = uuid4()
    user = User(
        id=user_id,
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test User"
    )

    assert user.id is not None
    assert isinstance(user.id, UUID)
    assert user.id == user_id


def test_base_model_id_auto_generation():
    """Test UUID is auto-generated for new models"""
    model = BaseModel()

    assert model.id is not None
    assert isinstance(model.id, uuid4().__class__)


def test_base_model_timestamps():
    """Test created_at and updated_at can be set"""
    now = datetime.utcnow()
    user = User(
        id=uuid4(),
        email="test2@example.com",
        hashed_password="hashed",
        full_name="Test User 2",
        created_at=now,
        updated_at=now
    )

    assert user.created_at is not None
    assert user.updated_at is not None
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)


def test_base_model_timestamps_auto():
    """Test created_at and updated_at are set automatically"""
    model = BaseModel()

    assert model.created_at is not None
    assert model.updated_at is not None
    assert isinstance(model.created_at, datetime)
    assert isinstance(model.updated_at, datetime)
    assert model.created_at <= datetime.utcnow()


# ====================================================================================
# PHASE 2: MEDIUM PRIORITY - Infrastructure Tests (8 tests)
# ====================================================================================
