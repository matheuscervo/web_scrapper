"""Script de teste rápido para verificar a coleta do Medium."""

import asyncio
from playwright.async_api import async_playwright

async def quick_test():
    print("🔍 Testando acesso ao Medium...")
    
    async with async_playwright() as p:
        browser_args = ["--disable-blink-features=AutomationControlled"]
        browser = await p.chromium.launch(headless=True, args=browser_args)
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        page = await context.new_page()
        
        try:
            # Tentar acessar página de tag
            url = "https://medium.com/tag/ux-design/recommended"
            print(f"📡 Acessando: {url}")
            
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(5)
            
            # Verificar título da página
            title = await page.title()
            print(f"📄 Título: {title}")
            
            # Buscar links de artigos
            links = await page.query_selector_all("a[href*='medium.com']")
            print(f"🔗 Links encontrados: {len(links)}")
            
            # Mostrar alguns links
            article_links = []
            for link in links[:20]:
                href = await link.get_attribute("href")
                if href and "/@" in href and len(href) > 50:
                    article_links.append(href)
            
            print(f"\n📚 Links de artigos potenciais:")
            for link in article_links[:5]:
                print(f"  • {link[:80]}...")
            
            print(f"\n✓ Teste concluído! {len(article_links)} links de artigos encontrados.")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(quick_test())
