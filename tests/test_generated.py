import pytest
from playwright.sync_api import expect

def test_heading_contains_example(healing_page):
    healing_page.goto("https://example.org/")
    heading = healing_page.locator("h1")
    expect(heading).to_contain_text("Example")
