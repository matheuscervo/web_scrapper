"""Teste detalhado de links"""
import asyncio
from playwright.async_api import async_playwright

async def test_links():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()
        
        # Página de arquivo com posts garantidos
        url = "https://medium.com/tag/ux-design/archive/2025/01/15"
        print(f"URL: {url}")
        
        await page.goto(url, wait_until="networkidle") # Usar networkidle para garantir que tudo carregou
        
        links = await page.eval_on_selector_all("a", "els => els.map(el => el.href)")
        print(f"Total hrefs: {len(links)}")
        
        print("Amostra de 20 links:")
        for l in links[:20]:
            print(f" - {l}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_links())
