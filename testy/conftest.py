import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session

from users_db import Base
from models import User
from api import app, get_session, hash_password


@pytest.fixture()
def setup_database():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def setup_test_data(setup_database):
    with Session(setup_database) as session:
        session.add_all([
            User(username="admin", hashed_password=hash_password("admin123"), roles="ROLE_ADMIN"),
            User(username="user", hashed_password=hash_password("user123"), roles="ROLE_USER"),
        ])
        session.commit()


@pytest.fixture()
def client(setup_database, setup_test_data):
    def override_get_session():
        s = Session(setup_database)
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()
