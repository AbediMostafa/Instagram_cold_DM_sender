from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(
        proxy={
            'server': "http://207.230.104.241:29842",
            'username': 'paichb',
            'password': 'yNckWHb3',
        },
        headless=False)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1')
    page = context.new_page()
    page.goto("https://www.instagram.com/")
    page.wait_for_timeout(1000000)
    page.get_by_role("button", name="Allow all cookies").click()
    page.get_by_label("Phone number, username, or email").click()
    page.get_by_label("Phone number, username, or email").fill("team33m11t")
    page.get_by_label("Password").click()
    page.get_by_label("Password").fill("far895tile620")
    page.get_by_role("button", name="Log in", exact=True).click()
    page.get_by_role("button", name="Save info").click()
    page.get_by_role("button", name="Turn On").click()
    page.get_by_role("link", name="team33m11t's profile picture Profile").click()
    page.get_by_role("link", name="Edit profile").click()
    page.get_by_placeholder("Bio").click()
    page.get_by_placeholder("Bio").fill("A girl with open wings")
    page.get_by_role("button", name="Submit").click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
