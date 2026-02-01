"""
collector.py - Módulo de coleta de links do Medium

Responsável por:
- Acessar páginas de tag do Medium via Playwright (Scroll Infinito)
- Realizar scroll para carregar conteúdo dinâmico
- Extrair URLs de artigos de 2025 (filtragem preliminar)
"""

import asyncio
import re
from datetime import datetime
from typing import List, Set, Optional
from playwright.async_api import async_playwright, Page, Browser

# Configurações
# Tentamos /latest para garantir ordem cronológica. Se redirecionar, OK.
MEDIUM_TAG_URL = "https://medium.com/tag/{tag}/latest"
SCROLL_PAUSE_TIME = 2.5
MAX_SCROLLS = 150
YEAR_CUTOFF = 2025


async def collect_links_from_tag(tag: str, headless: bool = True) -> List[str]:
    """
    Coleta links de artigos de uma tag específica via Scroll Infinito.
    """
    collected_urls: Set[str] = set()
    url = MEDIUM_TAG_URL.format(tag=tag)
    
    print(f"\n{'='*60}")
    print(f"🔍 Coletando artigos da tag: {tag}")
    print(f"📎 URL: {url}")
    print(f"{'='*60}\n")
    
    async with async_playwright() as p:
        # Argumentos anti-bot
        browser_args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-infobars",
            "--disable-dev-shm-usage",
            "--disable-browser-side-navigation",
            "--disable-gpu",
        ]
        
        browser = await p.chromium.launch(
            headless=headless,
            args=browser_args
        )
        
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US",
            timezone_id="America/Sao_Paulo",
        )
        
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        page = await context.new_page()
        
        try:
            print("📡 Acessando página...")
            # Timeout longo para evitar quebras em conexões lentas ou Cloudflare
            resp = await page.goto(url, wait_until="domcontentloaded", timeout=90000)
            
            # Verificar se foi redirecionado (algumas tags não têm /latest)
            final_url = page.url
            if "/latest" not in final_url and "medium.com" in final_url:
                print(f"ℹ Redirecionado para: {final_url} (Provavelmente sem feed 'latest')")
            
            await asyncio.sleep(5)
            
            # Verificar Cloudflare
            title = await page.title()
            if "Just a moment" in title or "Cloudflare" in title:
                print("⚠ Cloudflare detectado. Aguardando resolução...")
                await asyncio.sleep(15)
            
            scroll_count = 0
            previous_count = 0
            no_new_content_count = 0
            old_content_found = False
            
            while scroll_count < MAX_SCROLLS and not old_content_found:
                scroll_count += 1
                
                # Scroll suave para simular usuário
                await _smooth_scroll(page)
                
                # Extrair links
                new_urls, found_old = await _extract_article_links(page)
                
                # Se encontrou novos links
                if len(new_urls) > len(collected_urls):
                    added = len(new_urls) - len(collected_urls)
                    collected_urls.update(new_urls)
                    no_new_content_count = 0
                else:
                    no_new_content_count += 1
                
                # Se encontrou conteúdo velho (anterior a 2025)
                # Só paramos se estivermos no feed cronológico (/latest)
                # Se for feed Recommended, conteúdo velho pode aparecer mesmo antes de novos
                is_chronological = "/latest" in page.url
                
                if found_old and is_chronological:
                    print(f"\n⚠ Conteúdo de {YEAR_CUTOFF-1} encontrado. Parando (ordem cronológica).")
                    old_content_found = True
                    break
                
                # Critério de parada por falta de novos itens
                if no_new_content_count >= 6:
                    print("\n⚠ Sem novos itens após 6 scrolls. Parando.")
                    break
                
                print(f"📜 Scroll {scroll_count}: {len(collected_urls)} artigos coletados", end="\r")
                await asyncio.sleep(SCROLL_PAUSE_TIME)
            
            print(f"\n\n✓ Coleta finalizada: {len(collected_urls)} links encontrados")
            
        except Exception as e:
            print(f"\n❌ Erro durante coleta: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()
    
    return list(collected_urls)


async def _smooth_scroll(page: Page):
    """Realiza scroll suave."""
    await page.evaluate("""
        window.scrollBy({
            top: window.innerHeight * 0.8,
            behavior: 'smooth'
        });
    """)


async def _extract_article_links(page: Page) -> tuple[Set[str], bool]:
    valid_urls = set()
    found_old_content = False
    
    # Pegar TODOS os links da página via JS para garantir
    hrefs = await page.evaluate("""() => {
        return Array.from(document.querySelectorAll('a')).map(a => a.href);
    }""")
    
    for href in hrefs:
        if href and _is_article_url(href):
            normalized = _normalize_url(href)
            valid_urls.add(normalized)
    
    # Tentar detectar ano velho no texto visível da página (heurística simples)
    # Se acharmos muitas datas de 2024, avisamos
    # Isso é impreciso em feed misto, então usamos com cautela
    
    return valid_urls, found_old_content


def _is_article_url(url: str) -> bool:
    if not url: return False
    # Exclusões
    bad = ["/tag/", "/search", "/me/", "/about", "/followers", "/lists", "/topics", "?source=", "/archive", "signin", "signup"]
    if any(b in url.lower() for b in bad): return False
    
    # Padrões bons
    if "/@" in url and len(url) > 40: return True
    if re.search(r"-[a-f0-9]{8,12}$", url): return True
    
    return False


def _normalize_url(url: str) -> str:
    return url.split("?")[0].split("#")[0]
