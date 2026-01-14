import boto3
from config import AWS_DEFAULT_REGION

bedrock = boto3.client("bedrock-runtime", region_name=AWS_DEFAULT_REGION)

# Model - Claude Opus 4.5
MODEL_ID = "us.anthropic.claude-opus-4-5-20251101-v1:0"


def invoke_bedrock(prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
    response = bedrock.converse(
        modelId=MODEL_ID,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": max_tokens, "temperature": temperature},
    )
    return response["output"]["message"]["content"][0]["text"]


def invoke_bedrock_with_pdf(prompt: str, pdf_bytes: bytes, max_tokens: int = 4000, temperature: float = 0.1) -> str:
    message_content = [
        {
            "document": {
                "name": "paper",
                "format": "pdf",
                "source": {"bytes": pdf_bytes},
            }
        },
        {"text": prompt}
    ]

    response = bedrock.converse(
        modelId=MODEL_ID,
        messages=[{"role": "user", "content": message_content}],
        inferenceConfig={"maxTokens": max_tokens, "temperature": temperature},
    )
    return response["output"]["message"]["content"][0]["text"]
