import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from src.database import models
from src.repository.comments import get_comment
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
    test_comment = models.Comment(content="This is a test comment", user_id=1, post_id=1)
    test_comment2 = models.Comment(content="This is a bed comment", user_id=1, post_id=1, is_blocked=True)
    test_comment3 = models.Comment(
        content="This is a test comment", user_id=2, post_id=1)
    test_comment4 = models.Comment(content="This is a bed comment", user_id=2, post_id=1, is_blocked=True)
    session.add(test_user)
    session.add(test_post)
    session.add(test_post2)
    session.add(test_comment)
    session.add(test_comment2)
    session.add(test_comment3)
    session.add(test_comment4)
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
async def test_create_comment(client, session, token):
    comment_data = {"content": "Test comment"}
    response = client.post("api/comments/posts/1", json=comment_data, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Test comment"
    assert data["user_id"] == 2
    assert data["post_id"] == 1
    assert data["id"] == 5

    reply = session.query(models.Comment).filter(models.Comment.parent_comment == data["id"]).first()
    assert reply.id == 6
    assert reply.user_id == 1
    assert reply.post_id == 1
    assert reply.parent_comment == 5


@pytest.mark.asyncio
async def test_create_blocked_comment(client, session, mock_create_schedule_task, token):
    comment_data = {"content": "Fuck you bitch"}
    response = client.post("api/comments/posts/1", json=comment_data, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Fuck you bitch"
    assert data["user_id"] == 2
    assert data["post_id"] == 1
    assert data["id"] == 5
    assert data["is_blocked"] is True
    task, schedule_task = mock_create_schedule_task
    task.assert_not_called()
    schedule_task.assert_not_called()


@pytest.mark.asyncio
async def test_create_comment_post_not_found(client, session, token):

    comment_data = {"content": "Test comment"}
    response = client.post("api/comments/posts/3", json=comment_data, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Post not found"


@pytest.mark.asyncio
async def test_create_comment_post_blocked(client, session, token):
    comment_data = {"content": "Test comment"}
    response = client.post("api/comments/posts/2", json=comment_data, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "You can't create comment for blocked post"


@pytest.mark.asyncio
async def test_read_comments(client, session, token):

    response = client.get("api/comments/posts/1", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4
    assert data[0]["content"] == "This is a test comment"
    assert data[1]["content"] == "This is a bed comment"
    assert data[1]["is_blocked"] is True


@pytest.mark.asyncio
async def test_read_nonexistent_comments(client, session, token):

    response = client.get("api/comments/posts/2", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    data = response.json()

    assert data["detail"] == "Comments not found"


@pytest.mark.asyncio
async def test_update_comment(client, session, token):
    comment_data = {"content": "updated test comment"}
    response = client.patch("api/comments/3", json=comment_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "updated test comment"


@pytest.mark.asyncio
async def test_update_blocked_comment(client, session, token):
    comment_data = {"content": "updated test comment"}
    response = client.patch("api/comments/4", json=comment_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "You cannot update blocked comments"


@pytest.mark.asyncio
async def test_update_another_user_comment(client, session, token):
    comment_data = {"content": "updated test comment"}
    response = client.patch("api/comments/2", json=comment_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "You cannot update other users comments"


@pytest.mark.asyncio
async def test_update_nonexistent_comment(client, session, token):
    comment_data = {"content": "updated test comment"}
    response = client.patch("api/comments/5", json=comment_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Comments not found"


@pytest.mark.asyncio
async def test_delete_comment(client, session, token):
    response = client.delete("api/comments/3", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "This is a test comment"
    comment = await get_comment(session, 3)
    assert comment is None


@pytest.mark.asyncio
async def test_delete_nonexistent_comment(client, session, token):
    response = client.delete("api/comments/5", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Comments not found"


@pytest.mark.asyncio
async def test_delete_another_user_comment(client, session, token):
    response = client.delete("api/comments/2", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "You cannot delete other users comments"


@pytest.mark.asyncio
async def test_get_comments_breakdown(client, session, token):
    date_from = (datetime.utcnow() - timedelta(days=1))
    date_to = (datetime.utcnow() + timedelta(days=1))
    response = client.get(f"api/comments/comments-daily-breakdown/?date_from={date_from}&date_to={date_to}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["post_id"] == 1
    assert len(data[0]["stats"]) == 1
    assert data[0]["stats"][0]["total_comments"] == 4
    assert data[0]["stats"][0]["blocked_comments"] == 2


@pytest.mark.asyncio
async def test_get_no_comments_breakdown(client, session, token):
    date_from = (datetime.utcnow() - timedelta(days=2))
    date_to = (datetime.utcnow() - timedelta(days=1))
    response = client.get(f"api/comments/comments-daily-breakdown/?date_from={date_from}&date_to={date_to}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "There are no comments on posts during this period of time"


@pytest.mark.asyncio
async def test_get_comments_breakdown_with_incorrect_input(client, session, token):
    date_from = ("str")
    date_to = (datetime.utcnow() - timedelta(days=1))
    response = client.get(f"api/comments/comments-daily-breakdown/?date_from={date_from}&date_to={date_to}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 422
    data = response.json()
    print(data)
    assert data["detail"][0]["msg"] == 'Input should be a valid datetime or date, input is too short'