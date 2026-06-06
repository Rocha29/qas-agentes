#!/usr/bin/env python3
"""
rag_loader.py — Consolida os arquivos .md da knowledge_base/lojinha/
em um único context.md injetável no início de qualquer sessão.

Uso:
    python tools/rag_loader.py
    python tools/rag_loader.py --output caminho/customizado.md
    python tools/rag_loader.py --print   (imprime no stdout em vez de salvar)
"""

import argparse
import sys
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge_base" / "lojinha"
DEFAULT_OUTPUT = KNOWLEDGE_DIR / "context.md"

# Ordem de inclusão — do mais crítico para o mais detalhado
FILE_ORDER = [
    "setup.md",
    "ambiente.md",
    "endpoints.md",
    "bugs-conhecidos.md",
    "decisoes.md",
]

HEADER = """\
# Contexto da Lojinha API — Gerado automaticamente por rag_loader.py
# Injete este arquivo no início de qualquer sessão para recarregar o contexto completo.
# Fonte: knowledge_base/lojinha/

"""

SEPARATOR = "\n\n---\n<!-- Fonte: {filename} -->\n\n"


def load_files(directory: Path, order: list[str]) -> list[tuple[str, str]]:
    """Carrega arquivos na ordem definida, depois os restantes em ordem alfabética."""
    loaded = []
    seen = set()

    for filename in order:
        path = directory / filename
        if path.exists():
            loaded.append((filename, path.read_text(encoding="utf-8")))
            seen.add(filename)
        else:
            print(f"[AVISO] Arquivo não encontrado: {path}", file=sys.stderr)

    for path in sorted(directory.glob("*.md")):
        if path.name not in seen and path.name != "context.md":
            loaded.append((path.name, path.read_text(encoding="utf-8")))

    return loaded


def build_context(files: list[tuple[str, str]]) -> str:
    parts = [HEADER]
    for i, (filename, content) in enumerate(files):
        if i > 0:
            parts.append(SEPARATOR.format(filename=filename))
        parts.append(content.strip())
    parts.append("\n")
    return "".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Consolida knowledge_base/lojinha/ em context.md")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help=f"Arquivo de saída (padrão: {DEFAULT_OUTPUT})")
    parser.add_argument("--print", action="store_true", dest="print_only",
                        help="Imprime no stdout em vez de salvar")
    args = parser.parse_args()

    if not KNOWLEDGE_DIR.exists():
        print(f"[ERRO] Diretório não encontrado: {KNOWLEDGE_DIR}", file=sys.stderr)
        sys.exit(1)

    files = load_files(KNOWLEDGE_DIR, FILE_ORDER)
    if not files:
        print("[ERRO] Nenhum arquivo .md encontrado.", file=sys.stderr)
        sys.exit(1)

    context = build_context(files)

    if args.print_only:
        print(context)
        return

    output_path: Path = args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(context, encoding="utf-8")

    total_chars = len(context)
    total_kb = total_chars / 1024
    print(f"[OK] context.md gerado: {output_path}")
    print(f"     Arquivos incluídos : {len(files)}")
    print(f"     Tamanho total      : {total_kb:.1f} KB ({total_chars:,} caracteres)")
    print()
    print("Como usar em uma nova sessão:")
    print(f"  claude --system-prompt {output_path} 'sua pergunta aqui'")
    print()
    print("Ou copiar para o clipboard (macOS):")
    print(f"  cat {output_path} | pbcopy")


if __name__ == "__main__":
    main()
