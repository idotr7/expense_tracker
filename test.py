import pytest #type: ignore
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app import app, get_session


@pytest.fixture(name="session")  
def session_fixture():  
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session  


def test_create_hero(session: Session):  
    def get_session_override():
        return session  

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)

    response = client.post(
        "/users/", json={"name": "Ido", "email": "idodo@email.com", "password": "stgam123"}
    )
    app.dependency_overrides.clear()
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Lorin"
    assert data["email"] == "lorin@email.com"
    assert data["age"] is None
    assert data["id"] is not None