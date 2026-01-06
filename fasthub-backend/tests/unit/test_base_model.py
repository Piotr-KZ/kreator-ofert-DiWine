# ============================================================================

from app.models.base import BaseModel


def test_base_model_id_generation():
    """Test UUID is auto-generated for new models"""
    model = BaseModel()
    
    assert model.id is not None
    assert isinstance(model.id, uuid4().__class__)


def test_base_model_timestamps():
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
