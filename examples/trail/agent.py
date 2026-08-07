import asyncio
import os

MODEL = "openai/gpt-4o-mini"  # Set by benchmark config — do not change

CONCURRENT_REQUESTS = 5

DEPENDENCIES = []

USER_PROMPT_PREFIX = "Follow the taxonomy below carefully follow the instructions and provide the output in the same format as the example.\n\n# Taxonomy\n├── Reasoning Errors\n│   ├── Hallucinations\n│   │   ├── Language-only\n│   │   └── Tool-related (fabricating tool outputs/capabilities)\n│   ├── Information Processing\n│   │   ├── Poor Information Retrieval (Tried to find information that was not relevant to the task)\n│   │   └── Tool Output Misinterpretation (Made assumptions about the tool output or used the tool output in an incorrect context)\n│   ├── Decision Making\n│   │   ├── Incorrect Problem Identification (Misunderstood the overall task or the local task)\n│   │   └── Tool Selection Errors (Used the wrong tool for the task)\n│   └── Output Generation\n│       ├── Formatting Errors (Errors with formatting and execution of code or structuring of output in a specific format)\n│       └── Instruction Non-compliance (Failed to perform the task provided and instead did something else)\n├── System Execution Errors\n│   ├── Configuration\n│   │   ├── Tool Definition Issues (The tool was not defined correctly by the user or contains some errors that make it inconsistent with its description.)\n│   │   └── Environment Setup Errors (includes permission problems and inability to access resources or API keys)\n│   ├── API Issues\n│   │   ├── Rate Limiting (Like 429)\n│   │   ├── Authentication Errors (Like 401/403)\n│   │   ├── Service Errors (Like 500)\n│   │   └── Resource Not Found (Like 404)\n│   └── Resource Management\n│       ├── Resource Exhaustion (includes memory overflow)\n│       └── Timeout Issues (The system took too long to respond)\n├── Planning and Coordination Errors\n│    ├── Context Management\n│    │   ├── Context Handling Failures (includes window overflow and state tracking or forgetting important context)\n│    │   └── Resource Abuse (Called the tool excessively due to memory issues)\n│    └── Task Management\n│        ├── Goal Deviation (The system deviated from the task or the subtask)\n│        └── Task Orchestration (includes subtask coordination between agents and progress monitoring)\n\n- Based on the taxonomy above, analyze the LLM agent trace below and find errors in it.\n- You must be exhaustive and find all the errors in the trace. Only include the final subcategories of the taxonomy.\n- You must provide the output strictly in JSON format as shown below (do not wrap in markdown, do not output anything other than the JSON).\n\nTemplate:\n{\n    \"errors\": [\n        {\n            \"category\": \"[INSERT ERROR CATEGORY FROM TAXONOMY HERE]\",\n            \"location\": \"[INSERT LOCATION OF ERROR HERE]\",\n            \"evidence\": \"[INSERT EXTRACTED EVIDENCE HERE]\",\n            \"description\": \"[INSERT DETAILED ERROR DESCRIPTION HERE]\",\n            \"impact\": \"[INSERT IMPACT HERE]\"\n        }\n    ],\n    \"scores\": [\n        {\n            \"reliability_score\": 3,\n            \"reliability_reasoning\": \"...\",\n            \"security_score\": 5,\n            \"security_reasoning\": \"...\",\n            \"instruction_adherence_score\": 4,\n            \"instruction_adherence_reasoning\": \"...\",\n            \"plan_opt_score\": 3,\n            \"plan_opt_reasoning\": \"...\",\n            \"overall\": 3.75\n        }\n    ]\n}\n\nIf the trace has no errors:\n{\"errors\": [], \"scores\": [{\"reliability_score\": 5, \"reliability_reasoning\": \"...\", \"security_score\": 5, \"security_reasoning\": \"...\", \"instruction_adherence_score\": 5, \"instruction_adherence_reasoning\": \"...\", \"plan_opt_score\": 5, \"plan_opt_reasoning\": \"...\", \"overall\": 5}]}\n\nEnsure the output is strictly correct JSON with no additional text or markdown.\n\nThe data to analyze is as follows:\n\n"

# TRAIL span_description fields can exceed 50 K tokens; truncate to fit context.
MAX_CHARS = 12000


async def run_batch(inputs: list[str], api_key: str) -> list[str]:
    if not api_key:
        return ['{"errors":[],"scores":[]}'] * len(inputs)

    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

    async def _call(inp: str) -> str:
        async with semaphore:
            user_content = USER_PROMPT_PREFIX + inp[:MAX_CHARS]
            response = await client.chat.completions.create(
                model=MODEL,
                temperature=0,
                messages=[{"role": "user", "content": user_content}],
            )
            return (response.choices[0].message.content or "{}").strip()

    return list(await asyncio.gather(*(_call(inp) for inp in inputs)))
