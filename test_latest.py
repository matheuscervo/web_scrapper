import asyncio
from playwright.async_api import async_playwright

async def test_latest():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        page = await context.new_page()
        # Tentar /latest
        await page.goto("https://medium.com/tag/ux-design/latest", wait_until="networkidle", timeout=60000)
        
        print(f"Título: {await page.title()}")
        
        # Verificar ano nos posts (primeiros 5)
        # Medium costuma por data em span ou time
        dates = await page.evaluate("""
            () => Array.from(document.querySelectorAll('span')).map(s => s.innerText).filter(t => t.match(/202[0-9]|ago|Just now/)).slice(0, 10)
        """)
        print("Datas encontradas:", dates)
        
        # Verificar links
        links = await page.evaluate("""
            () => Array.from(document.querySelectorAll('a[href*="medium.com"]'))
                       .map(a => a.href)
                       .filter(h => h.includes("/@") || h.match(/-[a-f0-9]+$/))
                       .slice(0, 5)
        """)
        print("Links encontrados:", links)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_latest())
