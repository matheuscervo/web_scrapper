"""Testa acesso ao arquivo do Medium"""
import asyncio
from playwright.async_api import async_playwright

async def test_archive():
    print("🔍 Testando acesso ao Archive...")
    async with async_playwright() as p:
        # Mesmas configs
        browser_args = ["--disable-blink-features=AutomationControlled"]
        browser = await p.chromium.launch(headless=True, args=browser_args)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()
        
        url = "https://medium.com/tag/ux-design/archive/2025/01/15"
        print(f"📡 Acessando: {url}")
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(5)
            
            # Salvar HTML
            html = await page.content()
            with open("debug_archive_day.html", "w", encoding="utf-8") as f:
                f.write(html)
            
            # Debug links
            links = await page.query_selector_all("a")
            print(f"🔗 Total links: {len(links)}")
            
            # Procurar links de artigos com heurísticas
            article_links = []
            for link in links:
                href = await link.get_attribute("href")
                if href and ("/@" in href or "-[a-f0-9]" in href) and "medium.com" in href:
                    article_links.append(href)
            
            print(f"🔗 Links potenciais: {len(article_links)}")
            for l in article_links[:5]:
                print(f"  - {l}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_archive())
