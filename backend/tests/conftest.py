"""
Shared pytest fixtures.

Stubs sentence_transformers/anthropic at collection time so unit tests don't
require downloading model weights or an API key to run — CI should be fast
and free. Integration tests that need a real DB use the `test_db` fixture.
"""
import sys
import types

import numpy as np
import pytest

if "sentence_transformers" not in sys.modules:
    st_stub = types.ModuleType("sentence_transformers")

    class _FakeSentenceTransformer:
        def __init__(self, *args, **kwargs):
            pass

        def encode(self, texts, **kwargs):
            if isinstance(texts, list):
                return np.random.rand(len(texts), 384)
            return np.random.rand(384)

    class _FakeCrossEncoder:
        def __init__(self, *args, **kwargs):
            pass

        def predict(self, pairs):
            return [0.5] * len(pairs)

    st_stub.SentenceTransformer = _FakeSentenceTransformer
    st_stub.CrossEncoder = _FakeCrossEncoder
    sys.modules["sentence_transformers"] = st_stub

if "anthropic" not in sys.modules:
    sys.modules["anthropic"] = types.ModuleType("anthropic")


@pytest.fixture
def test_db():
    """Yields a SQLAlchemy session against the configured test database, with tables reset."""
    from app.core.database import Base, SessionLocal, engine

    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        Base.metadata.drop_all(bind=engine)
