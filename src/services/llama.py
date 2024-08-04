from llamaapi import LlamaAPI
from src.conf.config import settings


llama = LlamaAPI(settings.llama_api_key)


async def generate_reply(post_text, comment_text, user_name):
    api_request_json = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": (
                    f"Post by {user_name}: {post_text}\n"
                    f"Comment: {comment_text}\n"
                    "Reply as the author of the post, ensuring the reply is relevant to both the post and the comment."
                ),
            },
        ],
        "stream": False,
    }

    response = llama.run(api_request_json)
    if response.status_code == 200:
        response_data = response.json()
        if "choices" in response_data and len(response_data["choices"]) > 0:
            return response_data["choices"][0]["message"]["content"].strip()
    return "Thank you for your comment!"
