import pytest

@pytest.mark.asyncio
async def test_healing_cache(healing_page):
    # 1️⃣ Go to the default start page
    await healing_page.goto("https://example.org/")

    # 2️⃣ Click an intentionally wrong selector – it will be healed on the first run
    await healing_page.click(
        selector="a#old-more-info",                     # ❌ does NOT exist
        purpose="link with text 'More information...'"
    )

    # 3️⃣ Wait for navigation to the external site (the link points to iana.org)
    await healing_page.wait_for_load_state("load")

    # 4️⃣ Verify we landed on the expected URL
    assert "iana.org" in healing_page.url