from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.instagram.com/")
    page.get_by_role("button", name="Allow all cookies").click()
    page.get_by_label("Phone number, username, or email").click()
    page.get_by_label("Phone number, username, or email").fill("team33f")
    page.get_by_label("Password").click()
    page.get_by_label("Password").fill("far895tile620")
    page.get_by_role("button", name="Log in", exact=True).click()
    page.get_by_role("button", name="Save info").click()
    page.get_by_role("button", name="Turn On").click()
    page.get_by_role("link", name="team33f's profile picture Profile").click()
    page.get_by_role("button", name="Options").click()
    page.get_by_role("button", name="Settings and privacy").click()
    page.get_by_role("link", name="Facebook wordmark and family of apps logo Accounts Center Manage your connected experiences and account settings across Meta technologies. Personal details Password and security Ad preferences See more in Accounts Center").click()
    page.get_by_role("link", name="team33f\nInstagram").click()
    page.get_by_role("link", name="Name", exact=True).click()
    page.get_by_label("Name").click()
    page.get_by_label("Name").press("Control+a")
    page.get_by_label("Name").fill("Simara Sunthan")
    page.get_by_role("button", name="Done").click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
