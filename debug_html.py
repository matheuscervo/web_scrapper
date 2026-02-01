"""Script de debug para salvar HTML da página do Medium."""

import asyncio
from playwright.async_api import async_playwright

async def debug_html():
    print("🔍 Depurando HTML do Medium...")
    
    async with async_playwright() as p:
        # Mesmas configs do collector
        browser_args = ["--disable-blink-features=AutomationControlled"]
        browser = await p.chromium.launch(headless=True, args=browser_args)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        page = await context.new_page()
        
        try:
            url = "https://medium.com/tag/ux-design"
            print(f"📡 Acessando: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(5)
            
            # Salvar HTML
            html = await page.content()
            with open("debug_medium.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("✓ HTML salvo em debug_medium.html")
            
            # Tentar listar hrefs brutos
            links = await page.eval_on_selector_all("a", "els => els.map(el => el.href)")
            print(f"🔗 Total de links na página: {len(links)}")
            
            # Filtrar links que parecem artigos
            article_links = [l for l in links if "medium.com" in l and "/@" not in l and "-" in l.split("/")[-1]] # Heurística simples
            print(f"🔗 Links potenciais de artigo (filtro simples): {len(article_links)}")
            for l in article_links[:5]:
                print(f"  - {l}")

        except Exception as e:
            print(f"❌ Erro: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_html())
