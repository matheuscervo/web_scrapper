"""
main.py - Script principal do Coletor de Artigos do Medium

Projeto: Coletor de Artigos sobre UX + Inteligência Artificial (2025)

Este script orquestra todo o pipeline:
1. Coleta de links por tag
2. Extração de metadados
3. Filtragem por critérios (ano + tags)
4. Exportação dos resultados

Uso:
    python main.py                  # Executa pipeline completo
    python main.py --collect        # Apenas coleta links
    python main.py --parse          # Apenas extrai metadados
    python main.py --filter         # Apenas filtra e exporta
    python main.py --headful        # Executa com navegador visível
"""

import asyncio
import argparse
from datetime import datetime

# Módulos do projeto
import collector
import parser
import storage


# Configurações do projeto
CONFIG = {
    "tags": ["ux-design", "artificial-intelligence"],
    "ano": 2025,
    "headless": True
}


async def step_1_collect_links():
    """
    Etapa 1: Coleta de links das páginas de tag do Medium.
    
    Para cada tag configurada, navega pela página de tag,
    faz scroll para carregar conteúdo e extrai URLs de artigos.
    """
    print("\n" + "=" * 70)
    print("📥 ETAPA 1: COLETA DE LINKS")
    print("=" * 70)
    
    for tag in CONFIG["tags"]:
        print(f"\n🏷️  Tag: {tag}")
        
        links = await collector.collect_links_from_tag(
            tag=tag,
            headless=CONFIG["headless"]
        )
        
        if links:
            storage.save_raw_links(links, tag)
        else:
            print(f"⚠ Nenhum link coletado para a tag '{tag}'")
    
    print("\n✓ Etapa 1 concluída!")


async def step_2_extract_metadata():
    """
    Etapa 2: Extração de metadados de cada artigo.
    
    Combina links de todas as tags, remove duplicatas,
    e extrai metadados de cada artigo individualmente.
    """
    print("\n" + "=" * 70)
    print("📊 ETAPA 2: EXTRAÇÃO DE METADADOS")
    print("=" * 70)
    
    # Combinar links de ambas as tags
    print("\n📁 Carregando links salvos...")
    all_links = storage.merge_links_from_tags(CONFIG["tags"])
    
    if not all_links:
        print("⚠ Nenhum link encontrado. Execute a Etapa 1 primeiro.")
        return []
    
    # Processar cada artigo
    articles = await parser.process_articles_batch(
        urls=all_links,
        headless=CONFIG["headless"],
        delay_between=2.5
    )
    
    # Salvar resultados intermediários (todos os artigos, sem filtro)
    if articles:
        storage.save_filtered_articles(articles, "artigos_raw_2025")
        print(f"\n💾 Salvos {len(articles)} artigos em artigos_raw_2025.json")
    
    print("\n✓ Etapa 2 concluída!")
    return articles


def step_3_filter_and_export(articles: list = None):
    """
    Etapa 3: Filtragem e exportação final.
    
    Aplica filtros:
    - Ano de publicação = 2025
    - Presença de AMBAS as tags (regra AND)
    
    Exporta em JSON e CSV.
    """
    print("\n" + "=" * 70)
    print("🔍 ETAPA 3: FILTRAGEM E EXPORTAÇÃO")
    print("=" * 70)
    
    # Carregar artigos se não fornecidos
    if articles is None:
        print("\n📁 Carregando artigos salvos...")
        articles = storage.load_filtered_articles("artigos_raw_2025")
    
    if not articles:
        print("⚠ Nenhum artigo encontrado. Execute as etapas anteriores primeiro.")
        return
    
    print(f"\n📚 Total de artigos antes do filtro: {len(articles)}")
    
    # Aplicar filtros
    filtered = parser.filter_articles_by_criteria(
        articles=articles,
        required_tags=CONFIG["tags"],
        year=CONFIG["ano"]
    )
    
    print(f"📋 Artigos após filtro (ano={CONFIG['ano']} + ambas as tags): {len(filtered)}")
    
    if filtered:
        # Exportar resultados finais
        print("\n💾 Exportando resultados...")
        storage.save_filtered_articles(filtered, "artigos_filtrados_2025")
        
        # Exibir resumo
        print("\n" + "-" * 50)
        print("📑 RESUMO DOS ARTIGOS FILTRADOS:")
        print("-" * 50)
        
        for i, article in enumerate(filtered, 1):
            print(f"\n{i}. {article['titulo'][:60]}...")
            print(f"   👤 {article['autor']}")
            print(f"   📅 {article['data_publicacao']}")
            print(f"   🏷️  {', '.join(article['tags'][:5])}")
    else:
        print("\n⚠ Nenhum artigo passou nos critérios de filtro.")
        print("   Verifique se há artigos de 2025 com ambas as tags:")
        print(f"   - {CONFIG['tags'][0]}")
        print(f"   - {CONFIG['tags'][1]}")
    
    print("\n✓ Etapa 3 concluída!")
    return filtered


async def run_full_pipeline():
    """Executa o pipeline completo."""
    start_time = datetime.now()
    
    print("\n" + "🚀" * 30)
    print("     COLETOR DE ARTIGOS DO MEDIUM - UX + IA (2025)")
    print("🚀" * 30)
    print(f"\n⏰ Início: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🏷️  Tags: {', '.join(CONFIG['tags'])}")
    print(f"📅 Ano: {CONFIG['ano']}")
    
    # Etapa 1: Coleta
    await step_1_collect_links()
    
    # Etapa 2: Extração
    articles = await step_2_extract_metadata()
    
    # Etapa 3: Filtragem e Exportação
    filtered = step_3_filter_and_export(articles)
    
    # Resumo final
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "=" * 70)
    print("✅ PIPELINE CONCLUÍDO")
    print("=" * 70)
    print(f"⏱️  Duração total: {duration}")
    print(f"📊 Artigos finais: {len(filtered) if filtered else 0}")
    print(f"📁 Arquivos gerados:")
    print(f"   - data/artigos_filtrados_2025.json")
    print(f"   - data/artigos_filtrados_2025.csv")


def main():
    """Ponto de entrada com parsing de argumentos."""
    parser_args = argparse.ArgumentParser(
        description="Coletor de Artigos do Medium sobre UX + IA"
    )
    
    parser_args.add_argument(
        "--collect", 
        action="store_true",
        help="Apenas executa a coleta de links"
    )
    
    parser_args.add_argument(
        "--parse", 
        action="store_true",
        help="Apenas executa a extração de metadados"
    )
    
    parser_args.add_argument(
        "--filter", 
        action="store_true",
        help="Apenas executa a filtragem e exportação"
    )
    
    parser_args.add_argument(
        "--headful", 
        action="store_true",
        help="Executa com navegador visível (não headless)"
    )
    
    args = parser_args.parse_args()
    
    # Configurar modo headless
    if args.headful:
        CONFIG["headless"] = False
        print("🖥️  Modo: Navegador visível (headful)")
    
    # Executar etapa específica ou pipeline completo
    if args.collect:
        asyncio.run(step_1_collect_links())
    elif args.parse:
        asyncio.run(step_2_extract_metadata())
    elif args.filter:
        step_3_filter_and_export()
    else:
        # Pipeline completo
        asyncio.run(run_full_pipeline())


if __name__ == "__main__":
    main()
