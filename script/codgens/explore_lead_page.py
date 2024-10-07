import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.instagram.com/")
    page.get_by_role("button", name="Allow all cookies").click()
    page.get_by_label("Phone number, username, or").click()
    page.get_by_label("Phone number, username, or").fill("saram_ough")
    page.get_by_label("Phone number, username, or").press("Tab")
    page.get_by_label("Password").fill("far895tile620")
    page.get_by_label("Password").press("Enter")
    page.get_by_role("button", name="Save info").click()
    page.get_by_role("button", name="Turn On").click()
    page.get_by_role("link", name="Search Search").click()
    page.get_by_placeholder("Search").fill("socialmedia")
    page.get_by_role("link", name="learnwithakshat's profile picture learnwithakshat Social Media | Funnel Creator").click()
    page.get_by_role("link", name="1. Make your Content").click()
    page.get_by_role("button", name="Next", exact=True).click()
    page.get_by_role("button", name="digitalmukul_'s profile picture digitalmukul_ Verified Superb 151w 1 like Reply").get_by_role("button").nth(4).click()
    page.get_by_role("button", name="harmanentrepreneur's profile picture harmanentrepreneur Wow 😍 very interesting").get_by_role("button").nth(4).click()
    page.get_by_role("button", name="Next").click()
    page.locator("button").filter(has_text="Next").click()
    page.get_by_role("button", name="Next").click()
    page.get_by_role("button", name="Close").click()
    page.get_by_role("button", name="Follow").click()
    page.locator("li").filter(has_text="digitalsmakAhmad KhanFollow").get_by_role("button").nth(2).click()
    page.locator("li").filter(has_text="ashwaryaralhanऐश्वर्या |").get_by_role("button").nth(2).click()
    page.get_by_label("Next").click()
    page.get_by_label("Next").click()
    page.locator("li").filter(has_text="digi.mahieMahima🔹 Marketing").get_by_role("button").nth(2).click()
    page.get_by_label("Next").click()
    page.get_by_label("Next").click()
    page.get_by_role("link", name="1,485 followers").click()
    page.locator(".x1n2onr6 > div > div > .x1uvtmcs > div").click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
