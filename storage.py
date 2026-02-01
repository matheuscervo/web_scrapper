"""
storage.py - Módulo de armazenamento e exportação de dados

Responsável por:
- Salvar/carregar links brutos em JSON
- Exportar dados filtrados para JSON e CSV
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any

# Diretório de dados
DATA_DIR = Path(__file__).parent / "data"


def ensure_data_dir():
    """Garante que o diretório de dados existe."""
    DATA_DIR.mkdir(exist_ok=True)


def save_raw_links(links: List[str], tag: str) -> Path:
    """
    Salva links brutos coletados de uma tag específica.
    
    Args:
        links: Lista de URLs únicas
        tag: Nome da tag (ex: 'ux-design')
    
    Returns:
        Path do arquivo salvo
    """
    ensure_data_dir()
    filepath = DATA_DIR / f"raw_links_{tag}.json"
    
    data = {
        "tag": tag,
        "total_links": len(links),
        "links": links
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Salvos {len(links)} links em: {filepath}")
    return filepath


def load_raw_links(tag: str) -> List[str]:
    """
    Carrega links brutos de uma tag específica.
    
    Args:
        tag: Nome da tag
    
    Returns:
        Lista de URLs
    """
    filepath = DATA_DIR / f"raw_links_{tag}.json"
    
    if not filepath.exists():
        print(f"⚠ Arquivo não encontrado: {filepath}")
        return []
    
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return data.get("links", [])


def save_filtered_articles(articles: List[Dict[str, Any]], filename_base: str = "artigos_filtrados_2025") -> tuple:
    """
    Salva artigos filtrados em JSON e CSV.
    
    Args:
        articles: Lista de dicionários com metadados dos artigos
        filename_base: Nome base para os arquivos (sem extensão)
    
    Returns:
        Tuple com paths dos arquivos JSON e CSV
    """
    ensure_data_dir()
    
    json_path = DATA_DIR / f"{filename_base}.json"
    csv_path = DATA_DIR / f"{filename_base}.csv"
    
    # Salvar JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    print(f"✓ JSON salvo: {json_path}")
    
    # Salvar CSV
    if articles:
        # Campos para o CSV
        fieldnames = ["titulo", "autor", "data_publicacao", "tags", "tempo_leitura", "resumo", "fonte", "url"]
        
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            
            for article in articles:
                # Converter lista de tags para string separada por vírgula
                row = article.copy()
                if isinstance(row.get("tags"), list):
                    row["tags"] = ", ".join(row["tags"])
                writer.writerow(row)
        
        print(f"✓ CSV salvo: {csv_path}")
    else:
        print("⚠ Nenhum artigo para salvar no CSV")
    
    return json_path, csv_path


def load_filtered_articles(filename_base: str = "artigos_filtrados_2025") -> List[Dict[str, Any]]:
    """
    Carrega artigos filtrados do JSON.
    
    Args:
        filename_base: Nome base do arquivo
    
    Returns:
        Lista de artigos
    """
    json_path = DATA_DIR / f"{filename_base}.json"
    
    if not json_path.exists():
        return []
    
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def merge_links_from_tags(tags: List[str]) -> List[str]:
    """
    Combina links de múltiplas tags, removendo duplicatas.
    
    Args:
        tags: Lista de nomes de tags
    
    Returns:
        Lista de URLs únicas
    """
    all_links = set()
    
    for tag in tags:
        links = load_raw_links(tag)
        all_links.update(links)
        print(f"  • {tag}: {len(links)} links")
    
    unique_links = list(all_links)
    print(f"\n→ Total de links únicos: {len(unique_links)}")
    
    return unique_links
