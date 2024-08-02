import json

from src.conf.config import settings
from googleapiclient import discovery
from googleapiclient.errors import HttpError
import logging


def analyze_text(text: str) -> dict:
    client = discovery.build(
        "commentanalyzer",
        "v1alpha1",
        developerKey=settings.perspective_api_key,
        discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
        static_discovery=False,
    )

    analyze_request = {
        'comment': {'text': text},
        'requestedAttributes': {'TOXICITY': {}}
    }

    response = client.comments().analyze(body=analyze_request).execute()
    print(json.dumps(response, indent=2))
    return response


async def analyze_comment_content(content: str) -> bool:
    try:
        response = analyze_text(content)
        toxicity_score = response['attributeScores']['TOXICITY']['summaryScore']['value']
        return toxicity_score > 0.7
    except HttpError as e:
        logging.error(f"Perspective API error: {e}")
        return False
