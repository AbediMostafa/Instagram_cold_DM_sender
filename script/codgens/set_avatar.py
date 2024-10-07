from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.instagram.com/")
    page.get_by_role("button", name="Allow all cookies").click()
    page.get_by_label("Phone number, username, or email").fill("saram_ough")
    page.get_by_label("Password").fill("far895tile620")
    page.get_by_role("button", name="Log in", exact=True).click()
    page.get_by_role("button", name="Save info").click()
    page.get_by_role("button", name="Turn On").click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
