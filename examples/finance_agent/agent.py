import asyncio
import os

MODEL = "openai/gpt-4o-mini"  # Set by benchmark config — do not change

CONCURRENT_REQUESTS = 5

DEPENDENCIES = []

SYSTEM_PROMPT = "You are an expert financial analyst.\nRules:\n- Answer with ONLY the final answer — no explanation\n- For dollar amounts include $ sign and scale (K/M/B) if applicable\n- For percentages include % symbol\n- For company names use exact legal name"


async def run_batch(inputs: list[str], api_key: str) -> list[str]:
    if not api_key:
        return ["unknown"] * len(inputs)

    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

    async def _call(inp: str) -> str:
        async with semaphore:
            response = await client.chat.completions.create(
                model=MODEL,
                temperature=0,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": inp},
                ],
            )
            return (response.choices[0].message.content or "").strip()

    return list(await asyncio.gather(*(_call(inp) for inp in inputs)))
