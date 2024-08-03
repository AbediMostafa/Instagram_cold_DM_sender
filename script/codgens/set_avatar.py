from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.instagram.com/")
    page.get_by_role("button", name="Allow all cookies").click()
    page.get_by_label("Phone number, username, or email").click()
    page.get_by_label("Phone number, username, or email").fill("samir_404_trollinoo")
    page.get_by_label("Password").click()
    page.get_by_label("Password").fill("far895tile620")
    page.get_by_role("button", name="Log in", exact=True).click()
    page.get_by_role("button", name="Save info").click()
    page.get_by_role("button", name="Turn On").click()
    page.get_by_role("button", name="Follow").nth(1).click()
    page.get_by_role("button", name="Follow").nth(3).click()
    page.get_by_role("button", name="Follow").nth(4).click()
    page.get_by_role("button", name="Follow").first.click()
    page.get_by_role("link", name="samir_404_trollinoo's profile picture Profile").click()
    page.get_by_role("button", name="Change profile photo").click()
    page.get_by_role("button", name="Upload Photo").click()
    page.get_by_role("button", name="Upload Photo").set_input_files("FwulAYIXsAEepEP.jpg")

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
