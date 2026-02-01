from playwright.sync_api import sync_playwright

TAG_URL = "https://medium.com/tag/ux-design/archive"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(TAG_URL, wait_until="domcontentloaded")

        # TODO: esperar algo que indique que a lista carregou
        # page.wait_for_selector("...")

        # TODO: coletar links de artigos
        # links = page.locator("a").all() ...

        # TODO: filtrar para URLs que parecem posts e imprimir 5

        browser.close()

if __name__ == "__main__":
    main()
