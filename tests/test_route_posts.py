import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from src.database import models
from src.repository.posts import get_posts
from src.services.auth import auth_service


@pytest.fixture
def mock_create_schedule_task(mocker):
    mock_task = mocker.patch('src.services.scheduler.create_schedule_task', return_value=(AsyncMock(), []))
    mock_schedule_task = mocker.patch('src.services.scheduler.schedule_task')
    return mock_task, mock_schedule_task


@pytest.fixture(autouse=True)
def setup_data(session):
    test_user = models.User(id=1, username="Test", email="test@test.com", password="test", auto_reply_enabled=True, auto_reply_delay=0)
    test_post = models.Post(id=1, title="Test Post", content="This is a test post", user_id=1)
    test_post2 = models.Post(
        id=2, title="Test Post2", content="Bad content", user_id=1, is_blocked=True
    )
    test_post3 = models.Post(
        id=3, title="Test Post", content="This is a test post", user_id=2
    )
    test_comment = models.Comment(content="This is a test comment", user_id=1, post_id=1)
    test_comment2 = models.Comment(content="This is a bed comment", user_id=1, post_id=1, is_blocked=True)

    session.add(test_user)
    session.add(test_post)
    session.add(test_post2)
    session.add(test_post3)
    session.add(test_comment)
    session.add(test_comment2)
    session.commit()


@pytest.fixture(autouse=True)
def clean_db(session):
    models.Base.metadata.drop_all(bind=session.get_bind())
    models.Base.metadata.create_all(bind=session.get_bind())


@pytest.fixture()
def token(client, user, session):
    client.post("/api/auth/signup", json=user)

    response = client.post(
        "/api/auth/login",
        data={"username": user.get("email"), "password": user.get("password")},
    )
    data = response.json()
    return data["access_token"]


@pytest.fixture(autouse=True)
def mock_redis_db():
    with patch.object(auth_service, "redis_db") as redis_mock:
        redis_mock.get.return_value = None
        yield redis_mock


@pytest.mark.asyncio
async def test_create_post(client, session, token):
    post_data = {"title": "Test", "content": "Test post"}
    response = client.post("api/posts/", json=post_data, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Test post"
    assert data["user_id"] == 2
    assert data["id"] == 4
    assert data["is_blocked"] is False


@pytest.mark.asyncio
async def test_create_blocked_post(client, session, token):
    post_data = {"title": "Test", "content": "Fuck you bitch"}
    response = client.post("api/posts/", json=post_data, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Fuck you bitch"
    assert data["user_id"] == 2
    assert data["id"] == 4
    assert data["is_blocked"] is True


@pytest.mark.asyncio
async def test_create_post_not_authorized(client, session, token):
    post_data = {"title": "Test", "content": "Test post"}
    response = client.post("api/posts/", json=post_data)

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == 'Not authenticated'


@pytest.mark.asyncio
async def test_read_posts(client, session, token):
    response = client.get("api/posts/?skip=0&limit=5", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    assert data[0]["content"] == "This is a test post"
    assert data[1]["content"] == "Bad content"


@pytest.mark.asyncio
async def test_read_posts(client, session, token):
    response = client.get("api/posts/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "This is a test post"


@pytest.mark.asyncio
async def test_read_nonexistent_posts(client, session, token):
    response = client.get("api/posts/4", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Post not found"


@pytest.mark.asyncio
async def test_update_post(client, session, token):
    post_data = {"title": "updated title", "content": "updated test post"}
    response = client.patch("api/posts/3", json=post_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "updated title"
    assert data["content"] == "updated test post"


@pytest.mark.asyncio
async def test_update_post_title(client, session, token):
    post_data = {"title": "updated title", "content": ""}
    response = client.patch("api/posts/3", json=post_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "updated title"
    assert data["content"] == "This is a test post"


@pytest.mark.asyncio
async def test_update_post_content(client, session, token):
    post_data = {"title": "", "content": "updated test post"}
    response = client.patch("api/posts/3", json=post_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Post"
    assert data["content"] == "updated test post"


@pytest.mark.asyncio
async def test_update_another_user_post(client, session, token):
    post_data = {"title": "updated title", "content": "updated test post"}
    response = client.patch("api/posts/1", json=post_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "You cannot update other users posts"


@pytest.mark.asyncio
async def test_update_nonexistent_post(client, session, token):
    post_data = {"title": "updated title", "content": "updated test post"}
    response = client.patch("api/posts/4", json=post_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Post not found"


@pytest.mark.asyncio
async def test_delete_post(client, session, token):
    response = client.delete("api/posts/3", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Post"
    assert data["content"] == "This is a test post"
    posts = await get_posts(session)
    assert len(posts) == 2


@pytest.mark.asyncio
async def test_delete_nonexistent_post(client, session, token):
    response = client.delete("api/posts/4", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Post not found"


@pytest.mark.asyncio
async def test_delete_another_user_post(client, session, token):
    response = client.delete("api/posts/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "You cannot delete other users posts"

