"""
parser.py - Módulo de extração de metadados

Responsável por:
- Acessar artigos individuais do Medium
- Extrair metadados via JSON-LD (Schema.org)
- Fallback para HTML quando necessário
- Validar e estruturar dados
"""

import asyncio
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from playwright.async_api import async_playwright, Page

# Estrutura padrão de um artigo
ARTICLE_TEMPLATE = {
    "titulo": "",
    "autor": "",
    "data_publicacao": "",
    "tags": [],
    "tempo_leitura": "",
    "resumo": "",
    "fonte": "medium",
    "url": ""
}


async def extract_article_metadata(url: str, headless: bool = True) -> Optional[Dict[str, Any]]:
    """
    Extrai metadados de um artigo do Medium.
    
    Tenta primeiro usar JSON-LD (dados estruturados), com fallback para HTML.
    
    Args:
        url: URL do artigo
        headless: Se True, executa sem interface gráfica
    
    Returns:
        Dicionário com metadados ou None se falhar
    """
    async with async_playwright() as p:
        # Argumentos para evitar detecção
        browser_args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-infobars",
        ]
        
        browser = await p.chromium.launch(headless=headless, args=browser_args)
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        
        # Script para mascarar webdriver
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        page = await context.new_page()
        
        try:
            # Timeout maior e wait_until menos restritivo para evitar timeout em loads pesados
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(2)  # Aguardar carregamento de JS
            
            # Tentar extrair via JSON-LD primeiro
            metadata = await _extract_from_jsonld(page)
            
            # Se não encontrou JSON-LD, tentar via HTML
            if not metadata or not metadata.get("titulo"):
                metadata = await _extract_from_html(page)
            
            if metadata:
                metadata["url"] = url
                metadata["fonte"] = "medium"
            
            return metadata
            
        except Exception as e:
            print(f"  ✗ Erro ao processar {url}: {e}")
            return None
        
        finally:
            await browser.close()


async def _extract_from_jsonld(page: Page) -> Optional[Dict[str, Any]]:
    """
    Extrai metadados do JSON-LD (Schema.org) da página.
    
    Medium geralmente inclui dados estruturados para artigos.
    """
    try:
        # Buscar todas as tags script com type application/ld+json
        scripts = await page.query_selector_all('script[type="application/ld+json"]')
        
        for script in scripts:
            content = await script.inner_html()
            try:
                data = json.loads(content)
                
                # Pode ser uma lista ou objeto único
                if isinstance(data, list):
                    for item in data:
                        if item.get("@type") in ["Article", "NewsArticle", "BlogPosting"]:
                            return _parse_jsonld_article(item)
                elif data.get("@type") in ["Article", "NewsArticle", "BlogPosting"]:
                    return _parse_jsonld_article(data)
                elif "@graph" in data:
                    # Algumas páginas usam @graph para múltiplos schemas
                    for item in data["@graph"]:
                        if item.get("@type") in ["Article", "NewsArticle", "BlogPosting"]:
                            return _parse_jsonld_article(item)
            except json.JSONDecodeError:
                continue
        
        return None
        
    except Exception:
        return None


def _parse_jsonld_article(data: Dict) -> Dict[str, Any]:
    """Converte dados JSON-LD para o formato esperado."""
    article = ARTICLE_TEMPLATE.copy()
    
    # Título
    article["titulo"] = data.get("headline", data.get("name", ""))
    
    # Autor
    author = data.get("author")
    if isinstance(author, dict):
        article["autor"] = author.get("name", "")
    elif isinstance(author, list) and author:
        article["autor"] = author[0].get("name", "") if isinstance(author[0], dict) else str(author[0])
    elif isinstance(author, str):
        article["autor"] = author
    
    # Data de publicação
    date_published = data.get("datePublished", "")
    if date_published:
        article["data_publicacao"] = _normalize_date(date_published)
    
    # Resumo/descrição
    article["resumo"] = data.get("description", "")
    
    # Tags/keywords
    keywords = data.get("keywords")
    if isinstance(keywords, list):
        article["tags"] = keywords
    elif isinstance(keywords, str):
        article["tags"] = [k.strip() for k in keywords.split(",")]
    
    # Tempo de leitura (nem sempre disponível no JSON-LD)
    article["tempo_leitura"] = data.get("timeRequired", "")
    
    return article


async def _extract_from_html(page: Page) -> Optional[Dict[str, Any]]:
    """
    Fallback: extrai metadados do HTML quando JSON-LD não está disponível.
    """
    article = ARTICLE_TEMPLATE.copy()
    
    try:
        # Título - várias possibilidades
        title_selectors = [
            "h1",
            'meta[property="og:title"]',
            'meta[name="twitter:title"]',
            "title"
        ]
        
        for selector in title_selectors:
            element = await page.query_selector(selector)
            if element:
                if "meta" in selector:
                    article["titulo"] = await element.get_attribute("content") or ""
                else:
                    article["titulo"] = await element.inner_text()
                if article["titulo"]:
                    break
        
        # Autor - Medium geralmente usa link para perfil
        author_selectors = [
            'a[data-testid="authorName"]',
            'a[rel="author"]',
            'meta[name="author"]',
            'meta[property="article:author"]'
        ]
        
        for selector in author_selectors:
            element = await page.query_selector(selector)
            if element:
                if "meta" in selector:
                    article["autor"] = await element.get_attribute("content") or ""
                else:
                    article["autor"] = await element.inner_text()
                if article["autor"]:
                    break
        
        # Data de publicação
        date_selectors = [
            'meta[property="article:published_time"]',
            'time[datetime]',
            'meta[name="date"]'
        ]
        
        for selector in date_selectors:
            element = await page.query_selector(selector)
            if element:
                if selector == 'time[datetime]':
                    date_str = await element.get_attribute("datetime")
                else:
                    date_str = await element.get_attribute("content")
                if date_str:
                    article["data_publicacao"] = _normalize_date(date_str)
                    break
        
        # Resumo/descrição
        desc_element = await page.query_selector('meta[property="og:description"]')
        if desc_element:
            article["resumo"] = await desc_element.get_attribute("content") or ""
        
        # Tags - Medium exibe tags no final do artigo
        tag_elements = await page.query_selector_all('a[href*="/tag/"]')
        tags = set()
        for tag_el in tag_elements:
            tag_text = await tag_el.inner_text()
            if tag_text:
                tags.add(tag_text.strip().lower())
        article["tags"] = list(tags)
        
        # Tempo de leitura
        time_element = await page.query_selector('span:has-text(" min read")')
        if time_element:
            article["tempo_leitura"] = await time_element.inner_text()
        
        return article
        
    except Exception:
        return None


def _normalize_date(date_str: str) -> str:
    """
    Normaliza diferentes formatos de data para YYYY-MM-DD.
    """
    if not date_str:
        return ""
    
    # Tentar formato ISO
    try:
        # Remove timezone info se presente
        date_str = date_str.split("T")[0] if "T" in date_str else date_str
        date_str = date_str.split("+")[0]
        
        # Tentar parse como ISO
        dt = datetime.fromisoformat(date_str.replace("Z", ""))
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass
    
    # Tentar outros formatos comuns
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%B %d, %Y",
        "%b %d, %Y"
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    # Se não conseguiu converter, retornar como está
    return date_str


def filter_articles_by_criteria(
    articles: List[Dict[str, Any]], 
    required_tags: List[str],
    year: int = 2025
) -> List[Dict[str, Any]]:
    """
    Filtra artigos por ano e presença de todas as tags requeridas.
    
    Args:
        articles: Lista de artigos com metadados
        required_tags: Tags que devem estar presentes (regra AND)
        year: Ano de publicação requerido
    
    Returns:
        Lista de artigos que atendem aos critérios
    """
    filtered = []
    required_tags_lower = [tag.lower().replace("-", " ").replace("_", " ") for tag in required_tags]
    
    for article in articles:
        # Verificar ano
        date = article.get("data_publicacao", "")
        if not date or not date.startswith(str(year)):
            continue
        
        # Verificar tags (regra AND)
        article_tags_lower = [
            tag.lower().replace("-", " ").replace("_", " ") 
            for tag in article.get("tags", [])
        ]
        
        all_tags_present = all(
            any(req in tag or tag in req for tag in article_tags_lower)
            for req in required_tags_lower
        )
        
        if all_tags_present:
            filtered.append(article)
    
    return filtered


async def process_articles_batch(
    urls: List[str], 
    headless: bool = True,
    delay_between: float = 2.0
) -> List[Dict[str, Any]]:
    """
    Processa múltiplos artigos em sequência.
    
    Args:
        urls: Lista de URLs para processar
        headless: Se True, executa sem interface gráfica
        delay_between: Segundos entre cada requisição
    
    Returns:
        Lista de metadados extraídos
    """
    results = []
    total = len(urls)
    
    print(f"\n📖 Processando {total} artigos...")
    print("-" * 50)
    
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{total}] Extraindo: {url[:60]}...")
        
        metadata = await extract_article_metadata(url, headless)
        
        if metadata and metadata.get("titulo"):
            results.append(metadata)
            print(f"  ✓ {metadata['titulo'][:50]}...")
        else:
            print(f"  ✗ Não foi possível extrair metadados")
        
        if i < total:
            await asyncio.sleep(delay_between)
    
    print("-" * 50)
    print(f"✓ Processados: {len(results)} artigos com sucesso")
    
    return results


# Wrapper síncrono
def run_parser(url: str, headless: bool = True) -> Optional[Dict[str, Any]]:
    """Wrapper síncrono para extract_article_metadata."""
    return asyncio.run(extract_article_metadata(url, headless))
