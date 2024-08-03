from playwright.sync_api import sync_playwright


def run(playwright):
    device = playwright.devices['iPhone SE']
    browser = playwright.chromium.launch(headless=False)
    xiaomi_user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/534.24 XiaoMi/MiuiBrowser/13.30.1-gn'
    context = browser.new_context(user_agent=xiaomi_user_agent)
    page = context.new_page()
    page.goto('https://www.instagram.com')
    page.wait_for_timeout(1000000)
    # Your interactions with the page go here
    browser.close()

with sync_playwright() as playwright:
    run(playwright)


# from skimage import data, filters, io
#
#
# image = data.kidney()
# edges = filters.scharr(image)
# io.imshow_collection([image, edges])
# io.show()