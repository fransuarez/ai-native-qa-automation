---
name: QA Automation Rules
alwaysApply: true
description: Enforce project-specific conventions for AI-generated Playwright tests in this prototype.
---

# QA Automation Rules

## Fixture Usage
- All test functions MUST use the `healing_page` fixture provided by `pytest-self-healer`.
- Do NOT use the default `page` fixture from `pytest-playwright`.

## Purpose Parameter
- Every action on `healing_page` (e.g., `click`, `fill`, `goto`) MUST include a `purpose` string argument.
- The `purpose` must describe the user-facing intent of the target element, not its technical selector.
- Example:
  `await healing_page.click(selector="button#old-id", purpose="checkout submit button in the cart summary")`

Target page https://example.org contains: several <p> paragraphs and one link
with text "Learn more" (href to iana.org). It has NO <h1>, no forms, no buttons.
Only generate tests against elements that exist on this page.

## Generated Test Code
- Generated test files MUST be valid Python source code.
- Do NOT wrap the output in Markdown code fences (no ```python blocks).
- Do NOT include explanatory comments outside the test logic.

## Test Execution
- When running tests with self-healing enabled, always use:
  `--llm-provider=ollama --ollama-model=qwen2.5-coder:3b`
- The healing report will be written to `reports/`; inspect it if a test fails to heal.

## Model Reference
- The Groq model for test generation is `openai/gpt-oss-120b`.
- When calling Groq from scripts, ensure `max_tokens` is set to 800 or higher to accommodate the model's reasoning output.