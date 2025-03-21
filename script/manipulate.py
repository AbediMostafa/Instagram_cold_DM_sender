from playwright.sync_api import sync_playwright


def is_visible_by_text(page, text):
    return page.locator(f"text={text}").is_visible()


def accept_cookies():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.instagram.com/")

        if is_visible_by_text(page, "Allow the use of cookies") or is_visible_by_text(page,
                                                                                      "Allow all cookies") or is_visible_by_text(
                page, "Allow All Cookies"):

            try:
                page.locator('button', has_text='Allow all cookies').click(timeout=3000)
            except:
                page.locator('button', has_text='Allow All Cookies').click(timeout=3000)

        url = page.url.rstrip("/")
        print(url)
        page.wait_for_timeout(5000)  # Just to keep the browser open for a while
        browser.close()


accept_cookies()
