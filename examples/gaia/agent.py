import asyncio
import json
import os
import subprocess

MODEL = "openai/gpt-4o-mini"  # Set by benchmark config — do not change

MAX_STEPS = 5
CONCURRENT_REQUESTS = 5

DEPENDENCIES = []

SYSTEM_PROMPT = (
    "You are a general AI assistant. I will ask you a question.\n"
    "Use the python_interpreter tool for any calculation, counting, or data manipulation.\n"
    "When you have the final answer, end your response with:\n"
    "FINAL ANSWER: [YOUR FINAL ANSWER]\n"
    "YOUR FINAL ANSWER should be a number OR as few words as possible OR a comma separated list.\n"
    "If asked for a number: no commas, no units unless explicitly requested.\n"
    "If asked for a string: no articles, no abbreviations, write digits as plain text."
)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "python_interpreter",
            "description": (
                "Execute Python 3 code and return stdout + stderr. "
                "Use for arithmetic, unit conversions, string operations, counting, or any computation."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python 3 code to execute. Use print() to output results.",
                    }
                },
                "required": ["code"],
            },
        },
    }
]


def _run_python(code: str) -> str:
    """Run Python 3 code in a subprocess and return combined stdout + stderr."""
    try:
        result = subprocess.run(
            ["python3", "-c", code],
            capture_output=True,
            text=True,
            timeout=10,
        )
        out = result.stdout.strip()
        err = result.stderr.strip()
        if out and err:
            return f"{out}\n{err}"
        return out or err or "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: execution timed out (10s)"
    except Exception as exc:
        return f"Error: {exc}"


async def run_batch(inputs: list[str], api_key: str) -> list[str]:
    if not api_key:
        return ["unknown"] * len(inputs)

    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

    async def _call(inp: str) -> str:
        async with semaphore:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": inp},
            ]
            last_content = ""
            for _ in range(MAX_STEPS):
                response = await client.chat.completions.create(
                    model=MODEL,
                    temperature=0,
                    messages=messages,
                    tools=TOOLS,
                    tool_choice="auto",
                )

                msg = response.choices[0].message
                last_content = msg.content or ""

                if msg.tool_calls:
                    messages.append({
                        "role": "assistant",
                        "content": last_content,
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments,
                                },
                            }
                            for tc in msg.tool_calls
                        ],
                    })
                    for tc in msg.tool_calls:
                        args = json.loads(tc.function.arguments)
                        tool_result = _run_python(args.get("code", ""))
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": tool_result,
                        })
                else:
                    break

            if "FINAL ANSWER:" in last_content:
                last_content = last_content.split("FINAL ANSWER:")[-1].strip()
            return last_content.strip()

    return list(await asyncio.gather(*(_call(inp) for inp in inputs)))
