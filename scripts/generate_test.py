# scripts/generate_test.py
import os
import sys
import argparse
import ast
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq   # pip‑install groq‑sdk
import json

# ----------------------------------------------------------------------
# 1️⃣ Load .env (API key)
# ----------------------------------------------------------------------
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    sys.stderr.write("❌ Error: GROQ_API_KEY not found in .env\n")
    sys.exit(1)

# ----------------------------------------------------------------------
# 2️⃣ CLI argument: natural‑language description
# ----------------------------------------------------------------------
parser = argparse.ArgumentParser(
    description="Generate a pytest‑Playwright test from natural language using Groq."
)
parser.add_argument(
    "description",
    type=str,
    help="Natural‑language description of the test to generate."
)
args = parser.parse_args()
user_prompt = args.description.strip()

# ----------------------------------------------------------------------
# 3️⃣ Build system prompt – read the whole AGENTS.md file
# ----------------------------------------------------------------------
agents_path = Path(__file__).parent.parent / "AGENTS.md"
if not agents_path.is_file():
    sys.stderr.write("❌ Error: AGENTS.md not found.\n")
    sys.exit(1)

agents_content = agents_path.read_text(encoding="utf-8")
SYSTEM_PROMPT = f"""
You are an assistant that generates **valid Python pytest+Playwright** test code
based on a natural-language description. Follow **exactly** the rules from
the provided AGENTS.md file (included below). The output **must be only the
Python source code**, with **no markdown fences**, no surrounding text, and
no extra comments.

For every **interactive** action that supports a `purpose` parameter
(`click`, `fill`, `check`, `select_option`, etc.), include a descriptive
`purpose` string that explains the user-facing intent of the element.

=== EXAMPLE (specific test) ==============================================
@pytest.mark.asyncio
async def test_learn_more_link(healing_page):
    await healing_page.goto("https://example.org")
    await healing_page.click(
        selector="a#old-learn-more",
        purpose="‘Learn more’ link to the IANA example domains help page",
    )
    await healing_page.wait_for_load_state()
    assert "iana.org" in healing_page.url
=======================================================================

{agents_content}
"""

# ----------------------------------------------------------------------
# 4️⃣ Choose the model – try the requested one, fall back if it’s missing
# ----------------------------------------------------------------------
# Primary model required by the new spec
PRIMARY_MODEL = "openai/gpt-oss-120b"
# Fallback that works for almost everyone
FALLBACK_MODEL = "openai/gpt-oss-20b"

client = Groq(api_key=api_key)

def try_model(model_name: str) -> str:
    """Attempt a single‑call to the model to see if it exists."""
    try:
        # We do a *tiny* dry‑run (max_tokens=1) just to test accessibility.
        _ = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "system", "content": "ping"}],
            temperature=0.0,
            max_tokens=1,
            stream=False,
        )
        return model_name
    except Exception as exc:               # ← catch any Groq‑related error
            # If the error indicates that the requested resource was not
            # found (status code 404), treat it as a “no test” situation.
            if getattr(exc, "status_code", None) == 404:
                return None # type: ignore
            # For all other Groq errors, surface the problem.
            raise

# Try primary, otherwise fall back
selected_model = try_model(PRIMARY_MODEL)
if not selected_model:
    sys.stderr.write(
        f"⚠️  Model `{PRIMARY_MODEL}` not available – falling back to `{FALLBACK_MODEL}`.\n"
    )
    selected_model = FALLBACK_MODEL

# ----------------------------------------------------------------------
# 5️⃣ Call Groq – generate the test
# ----------------------------------------------------------------------
response = client.chat.completions.create(
    model=selected_model,
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": user_prompt},
    ],
    temperature=0.0,
    max_tokens=1200,   # generous room for a full test file
    stream=False,
)

generated_code = response.choices[0].message.content

# ----------------------------------------------------------------------
# 6️⃣ Clean the response – ensure it is *pure* Python
# ----------------------------------------------------------------------
assert generated_code is not None
generated_code = generated_code.strip()
if generated_code.startswith("```"):
    # Strip possible fences (```python, ``` etc.)
    lines = generated_code.splitlines()
    if lines[0].lstrip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].lstrip().startswith("```"):
        lines = lines[:-1]
    generated_code = "\n".join(lines).strip()

# ----------------------------------------------------------------------
# 7️⃣ Validate Python syntax
# ----------------------------------------------------------------------
try:
    ast.parse(generated_code)
except SyntaxError as exc:
    sys.stderr.write(
        f"❌ Generated code is not valid Python:\n{exc}\n---\n"
        "Full response was:\n"
        f"{generated_code}\n"
    )
    sys.exit(1)

# ----------------------------------------------------------------------
# 8️⃣ Write the file
# ----------------------------------------------------------------------
output_path = Path(__file__).parent.parent / "tests" / "test_generated.py"
output_path.write_text(generated_code + "\n")
print(f"✅ Test generated successfully → {output_path}")

sys.exit(0)