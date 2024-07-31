import asyncio

import google.generativeai as genai
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.database import models
from src.repository import users as repository_users
from src.repository import comments as repository_comments


def initialize_gemini_client():
    genai.configure(api_key=settings.google_api_key)
    return genai.GenerativeModel('gemini-1.5-flash')


model = initialize_gemini_client()


async def generate_ai_response(comment_content: str, post_content: str) -> str:
    prompt = f"Generate a relevant response to the comment: '{comment_content}' considering the post content: '{post_content}'"

    response = model.generate_content(
        contents=prompt
    )

    ai_response = response.text
    print(ai_response)
    return ai_response


async def schedule_auto_reply(post_owner_id: int, comment_id: int, db: Session, delay):
    print(f"Executing scheduled task for comment {comment_id}")
    db_comment = await repository_comments.get_comment(db, comment_id)
    db_post_owner = await repository_users.get_user_by_id(post_owner_id, db)
    if db_post_owner.auto_reply_enabled:
        reply_content = await generate_ai_response(db_comment.content, db_comment.post.content)
        db_reply = models.Comment(
            post_id=db_comment.post_id,
            user_id=post_owner_id,
            content=reply_content,
            parent_comment=db_comment.id
        )
        db.add(db_reply)
        db.commit()
        db.refresh(db_reply)
        print(f"Auto reply created for comment {comment_id}")





