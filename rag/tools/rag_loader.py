#!/usr/bin/env python3
"""
RAG Loader — Consolida knowledge_base/lojinha/ em um único context.md
Uso: python tools/rag_loader.py
"""

from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
LOJINHA_KB = BASE_DIR / "knowledge_base" / "lojinha"
OUTPUT = BASE_DIR / ".claude" / "lojinha-context.md"

# Ordem de prioridade dos arquivos
FILE_ORDER = [
    "context.md",       # resumo compacto — sempre primeiro
    "setup.md",         # ambiente e dependências
    "endpoints.md",     # endpoints mapeados
    "bugs-conhecidos.md", # gotchas e bugs
    "decisoes.md",      # decisões de arquitetura
]

def load_rag():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    sections = []
    for filename in FILE_ORDER:
        filepath = LOJINHA_KB / filename
        if filepath.exists():
            content = filepath.read_text(encoding="utf-8")
            sections.append(content)
            print(f"✅ Carregado: {filename}")
        else:
            print(f"⚠️  Não encontrado: {filename}")

    # Adiciona qualquer outro .md não listado acima
    for filepath in sorted(LOJINHA_KB.glob("*.md")):
        if filepath.name not in FILE_ORDER:
            content = filepath.read_text(encoding="utf-8")
            sections.append(content)
            print(f"✅ Carregado (extra): {filepath.name}")

    consolidated = "\n\n---\n\n".join(sections)
    OUTPUT.write_text(consolidated, encoding="utf-8")

    print(f"\n📄 RAG consolidado em: {OUTPUT}")
    print(f"📊 Total: {len(consolidated):,} caracteres | {len(sections)} arquivos")

if __name__ == "__main__":
    load_rag()
