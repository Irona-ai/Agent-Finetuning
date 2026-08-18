---
name: smoke-test
description: "Validate agent.py, eval.py, and dataset.json locally with a live dry-run before any Studio endpoint is called. Gates /create-agent-finetuning. Run standalone to debug file issues."
allowed-tools: Bash, Read
metadata:
  author: protege
  version: 2.0.0
  category: agent-optimization
  tags: [smoke-test, validation, dry-run, agent-finetuning, protege]
---

# Smoke Test

**Always runs before any Studio network call.** Catches broken files, bad signatures, and agent runtime errors before spending money on E2B sandboxes.

## When Invoked

- Explicitly: user types `/smoke-test` or asks to validate their files
- Automatically: as the first step inside `/create-agent-finetuning` — if smoke-test fails, the job is NOT submitted

## Steps

Run all steps in order. Any failure → print clear error with the failing check name, stop. No partial pass.

### Step 1 — Signature check

```bash
# agent.py must contain run_batch
grep -n "async def run_batch" agent.py || { echo "FAIL [signature] agent.py missing 'async def run_batch(inputs, api_key)'"; exit 1; }

# eval.py must contain score
grep -n "def score" eval.py || { echo "FAIL [signature] eval.py missing 'def score(expected, predicted)'"; exit 1; }
```

### Step 2 — Syntax check

```bash
python3 -c "
import ast, sys
for f in ['agent.py', 'eval.py']:
    try:
        ast.parse(open(f).read())
        print(f'  OK  {f}')
    except SyntaxError as e:
        print(f'FAIL [syntax] {f}:{e.lineno}: {e.msg}')
        sys.exit(1)
"
```

### Step 3 — Dataset check

```bash
python3 -c "
import json, sys
try:
    data = json.load(open('dataset.json'))
except Exception as e:
    print(f'FAIL [dataset] JSON parse error: {e}'); sys.exit(1)

if not isinstance(data, list):
    print('FAIL [dataset] must be a JSON array'); sys.exit(1)
if len(data) < 10:
    print(f'FAIL [dataset] {len(data)} items — minimum 10 required'); sys.exit(1)
for i, row in enumerate(data[:5]):
    if 'input' not in row or 'answer' not in row:
        print(f'FAIL [dataset] row {i} missing input/answer keys'); sys.exit(1)
print(f'  OK  dataset.json — {len(data)} items')
"
```

### Step 4 — Agent dry-run (no API key)

```bash
python3 -c "
import asyncio, importlib.util, json, sys

spec = importlib.util.spec_from_file_location('agent', 'agent.py')
mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
except Exception as e:
    print(f'FAIL [agent-import] {e}'); sys.exit(1)

try:
    result = asyncio.run(mod.run_batch(['smoke test input'], ''))
except Exception as e:
    print(f'FAIL [agent-run] {e}'); sys.exit(1)

if not isinstance(result, list) or len(result) != 1:
    print(f'FAIL [agent-run] run_batch must return list[str] of same length as inputs; got {type(result)}'); sys.exit(1)

print(f'  OK  agent dry-run -> {json.dumps(result)}')
"
```

### Step 5 — Eval dry-run

```bash
python3 -c "
import importlib.util, sys

spec = importlib.util.spec_from_file_location('eval', 'eval.py')
mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
except Exception as e:
    print(f'FAIL [eval-import] {e}'); sys.exit(1)

try:
    s = mod.score('expected answer', 'expected answer')
except Exception as e:
    print(f'FAIL [eval-run] {e}'); sys.exit(1)

if not isinstance(s, (int, float)) or not (0.0 <= float(s) <= 1.0):
    print(f'FAIL [eval-run] score() must return float 0.0–1.0; got {s!r}'); sys.exit(1)

print(f'  OK  eval dry-run -> score={float(s):.3f}')
"
```

### Step 6 — Dataset spot-run (first sample, no API key)

```bash
python3 -c "
import asyncio, importlib.util, json, sys

data = json.load(open('dataset.json'))
sample = data[0]
inp, expected = sample['input'], sample['answer']

agent_spec = importlib.util.spec_from_file_location('agent', 'agent.py')
agent_mod = importlib.util.module_from_spec(agent_spec)
agent_spec.loader.exec_module(agent_mod)

eval_spec = importlib.util.spec_from_file_location('eval', 'eval.py')
eval_mod = importlib.util.module_from_spec(eval_spec)
eval_spec.loader.exec_module(eval_mod)

predicted_list = asyncio.run(agent_mod.run_batch([inp], ''))
predicted = predicted_list[0]
s = eval_mod.score(expected, predicted)

print(f'  input:     {inp[:80]}')
print(f'  expected:  {expected[:80]}')
print(f'  predicted: {predicted[:80]}')
print(f'  score:     {float(s):.3f}')
print(f'  OK  spot-run complete')
"
```

## Success Output

```
  OK  agent.py
  OK  eval.py
  OK  dataset.json — 42 items
  OK  agent dry-run -> ["unknown"]
  OK  eval dry-run -> score=1.000
  input:     What is the capital of France?
  expected:  Paris
  predicted: unknown
  score:     0.000
  OK  spot-run complete

Smoke test passed. Safe to submit job.
```

## Common Failures

| Error | Cause | Fix |
|-------|-------|-----|
| `FAIL [signature] agent.py missing 'async def run_batch'` | Wrong function name/signature | Rename to `async def run_batch(inputs, api_key)` |
| `FAIL [syntax] agent.py:12: invalid syntax` | Python syntax error | Fix the line shown |
| `FAIL [dataset] 7 items — minimum 10 required` | Too few samples | Add more rows to dataset.json |
| `FAIL [agent-import] ModuleNotFoundError: openai` | Missing dependency | Add to `DEPENDENCIES` list or install locally |
| `FAIL [agent-run] run_batch must return list[str]` | Wrong return type | Return `list(await asyncio.gather(...))` |
