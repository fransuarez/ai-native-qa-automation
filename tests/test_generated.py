import pytest
from playwright.async_api import expect

@pytest.mark.asyncio
async def test_heading_contains_example(healing_page):
    await healing_page.goto("https://example.org/")
    heading = healing_page.locator("text=Example")
    await expect(heading).to_be_visible()
