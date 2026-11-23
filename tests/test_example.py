import pytest

@pytest.mark.asyncio
async def test_example_domain(healing_page):
    # 1️⃣ Open the page (no purpose argument needed for goto)
    await healing_page.goto("https://example.org")

    # 2️⃣ Click a deliberately wrong selector – this will trigger healing
    await healing_page.click(
        selector="button#old-submit-id",
        purpose="link to learn more about Example Domain"
    )

    # 3️⃣ Verify the title still contains “Example”
    title = await healing_page.title()
    assert "Example" in title
