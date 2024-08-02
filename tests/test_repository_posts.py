import pytest
from src import schemas
from src.database import models
from src.repository import posts as repository_posts


@pytest.fixture(autouse=True)
def clean_db(session):
    models.Base.metadata.drop_all(bind=session.get_bind())
    models.Base.metadata.create_all(bind=session.get_bind())


@pytest.mark.asyncio
async def test_create_post(client, session):
    post_data = schemas.PostCreate(title="Test", content="Test post")
    user_id = 1

    response = await repository_posts.create_post(session, post_data, user_id)

    assert response.content == "Test post"
    assert response.user_id == user_id
    assert not response.is_blocked


@pytest.mark.asyncio
async def test_get_posts(client, session):
    post_data = schemas.PostCreate(title="Test", content="Test post")
    post_data1 = schemas.PostCreate(title="Test1", content="Test post1")

    await repository_posts.create_post(session, post_data, 1)
    await repository_posts.create_post(session, post_data1, 2)

    posts = await repository_posts.get_posts(session, skip=0, limit=10)

    assert len(posts) == 2
    assert posts[0].content == "Test post"
    assert posts[1].content == "Test post1"


@pytest.mark.asyncio
async def test_get_post(client, session):
    post_data = schemas.PostCreate(title="Test", content="Test post")

    post = await repository_posts.create_post(session, post_data, 1)
    fetched_post = await repository_posts.get_post(session, post.id)

    assert fetched_post.id == post.id
    assert fetched_post.content == post.content

