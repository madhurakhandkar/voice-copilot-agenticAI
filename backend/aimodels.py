import boto3
import json
from botocore.exceptions import ClientError

# Create Bedrock client once
client = boto3.client("bedrock-runtime", region_name="us-east-1")

def claude3(system_prompt, conversation_history, max_tokens=500, temperature=0.7):

    model_id = "anthropic.claude-3-haiku-20240307-v1:0"

    request_payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "system": system_prompt,
        "messages": conversation_history
    }

    try:
        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps(request_payload)
        )

        model_response = json.loads(response["body"].read())
        assistant_reply = model_response["content"][0]["text"]

        return assistant_reply

    except (ClientError, Exception) as e:
        return f"ERROR: {e}"
    



def claude3_tuff(system_prompt, conversation_history, max_tokens=500, temperature=0.3):
    """
    system_prompt: string
    conversation_history: list of Anthropic-format messages
    returns: parsed JSON dict
    """

    model_id ="anthropic.claude-3-haiku-20240307-v1:0"

    # 🔥 Force strict JSON output
    json_enforcer = """
You MUST return valid JSON only.
Do NOT include markdown.
Do NOT include backticks.
Do NOT include explanations outside the JSON.

Return exactly this schema:

{
  "current_step": "string",
  "action_status": "correct | premature | incorrect | repeated",
  "next_action": "string",
  "explanation": "string"
}

ACTION_STATUS must be one of:
correct, premature, incorrect, repeated
"""

    request_payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "system": system_prompt + "\n\n" + json_enforcer,
        "messages": conversation_history
    }

    try:
        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps(request_payload)
        )

        model_response = json.loads(response["body"].read())
        assistant_text = model_response["content"][0]["text"]

        # 🔥 Parse JSON safely
        parsed_output = json.loads(assistant_text)

        return parsed_output

    except json.JSONDecodeError:
        return {
            "error": "Model did not return valid JSON",
            "raw_output": assistant_text
        }

    except (ClientError, Exception) as e:
        return {"error": str(e)}