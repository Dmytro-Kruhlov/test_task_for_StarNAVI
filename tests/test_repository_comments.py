import pytest
from datetime import datetime, timedelta
from src import schemas
from src.database import models
from src.repository import comments as repository_comments




@pytest.fixture(autouse=True)
def clean_db(session):
    models.Base.metadata.drop_all(bind=session.get_bind())
    models.Base.metadata.create_all(bind=session.get_bind())


@pytest.mark.asyncio
async def test_create_comment(client, session):
    comment_data = schemas.CommentCreate(content="Test comment")
    user_id = 1
    post_id = 1

    response = await repository_comments.create_comment(session, comment_data, post_id, user_id)

    assert response.content == "Test comment"
    assert response.user_id == user_id
    assert response.post_id == post_id
    assert not response.is_blocked


@pytest.mark.asyncio
async def test_get_comments_by_post(client, session):
    post_id = 1
    user_id = 1
    comment_data_1 = schemas.CommentCreate(content="Test comment 1")
    comment_data_2 = schemas.CommentCreate(content="Test comment 2")

    await repository_comments.create_comment(session, comment_data_1, post_id, user_id)
    await repository_comments.create_comment(session, comment_data_2, post_id, user_id)

    comments = await repository_comments.get_comments_by_post(session, post_id)

    assert len(comments) == 2
    assert comments[0].content == "Test comment 1"
    assert comments[1].content == "Test comment 2"


@pytest.mark.asyncio
async def test_get_comment(client, session):
    post_id = 1
    user_id = 1
    comment_data = schemas.CommentCreate(content="Test comment")

    created_comment = await repository_comments.create_comment(session, comment_data, post_id, user_id)
    fetched_comment = await repository_comments.get_comment(session, created_comment.id)

    assert fetched_comment.id == created_comment.id
    assert fetched_comment.content == created_comment.content


@pytest.mark.asyncio
async def test_get_comments_breakdown(client, session):
    post_id = 1
    user_id = 1
    comment_data_1 = schemas.CommentCreate(content="Test comment 1")
    comment_data_2 = schemas.CommentCreate(content="Test comment 2")
    comment_data_3 = schemas.CommentCreate(content="Test comment 3")

    await repository_comments.create_comment(session, comment_data_1, post_id, user_id)
    await repository_comments.create_comment(session, comment_data_2, post_id, user_id)
    comment3 = await repository_comments.create_comment(session, comment_data_3, post_id, user_id)
    await repository_comments.block_comment(session, comment3.id)
    date_from = datetime.utcnow() - timedelta(days=1)
    date_to = datetime.utcnow() + timedelta(days=1)

    breakdown = await repository_comments.get_comments_breakdown(session, date_from, date_to)

    assert len(breakdown) == 1
    assert breakdown[0]["post_id"] == post_id
    assert len(breakdown[0]["stats"]) > 0
    assert breakdown[0]["stats"][0]["total_comments"] == 3
    assert breakdown[0]["stats"][0]["blocked_comments"] == 1

