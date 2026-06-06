#!/usr/bin/env python3
"""
collect.py — Coleta metadados e transcrições dos canais QA brasileiros.

Uso:
  python tools/collect.py                                  # todos os autores, só metadados
  python tools/collect.py --author julio-de-lima          # autor específico
  python tools/collect.py --transcribe                    # inclui transcrição com Whisper
  python tools/collect.py --author fernando-papito --transcribe
  python tools/collect.py --max-duration 3600             # ignora vídeos > 1h
  python tools/collect.py --force                         # reprocessa mesmo se já existir
  python tools/collect.py --verbose                       # logs detalhados
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table

console = Console()

ROOT = Path(__file__).parent.parent
KNOWLEDGE_BASE = ROOT / "knowledge_base"
SOURCES_FILE = Path(__file__).parent / "sources.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text[:80]


def load_sources() -> dict:
    with open(SOURCES_FILE, encoding="utf-8") as f:
        return json.load(f)


def ensure_dirs(author_id: str) -> Path:
    author_dir = KNOWLEDGE_BASE / author_id
    (author_dir / "transcripts").mkdir(parents=True, exist_ok=True)
    return author_dir


# ---------------------------------------------------------------------------
# 1. Coleta de metadados via yt-dlp
# ---------------------------------------------------------------------------

def _channel_videos_url(channel_url: str) -> str:
    """Garante que a URL aponta para /videos do canal, não para as playlists."""
    url = channel_url.rstrip("/")
    if not url.endswith("/videos"):
        url += "/videos"
    return url


def fetch_videos(channel_url: str, verbose: bool = False) -> list[dict]:
    """Retorna lista de dicts com metadados de cada vídeo do canal."""
    videos_url = _channel_videos_url(channel_url)
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--dump-single-json",
        "--no-warnings",
        videos_url,
    ]
    if verbose:
        console.print(f"  [dim]$ {' '.join(cmd)}[/dim]")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        console.print(f"  [red]Erro ao coletar canal:[/red] {result.stderr[:300]}")
        return []

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        console.print("  [red]Resposta inválida do yt-dlp[/red]")
        return []

    entries = data.get("entries", [])
    # Se retornou sub-playlists em vez de vídeos, expandir o primeiro nível
    if entries and entries[0].get("_type") == "playlist":
        console.print("  [dim]Expandindo sub-playlists...[/dim]")
        expanded = []
        for playlist in entries:
            sub_cmd = cmd[:-1] + [playlist.get("url") or playlist.get("webpage_url", "")]
            sub_result = subprocess.run(sub_cmd, capture_output=True, text=True)
            try:
                sub_data = json.loads(sub_result.stdout)
                expanded.extend(sub_data.get("entries", []))
            except json.JSONDecodeError:
                pass
        entries = expanded

    videos = []
    for e in entries:
        if not e:
            continue
        video_id = e.get("id", "")
        # Ignorar entradas que não são vídeos reais (IDs de canal, etc.)
        if not video_id or len(video_id) != 11:
            continue
        videos.append({
            "id": video_id,
            "title": e.get("title", ""),
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "description": (e.get("description") or "").strip()[:500],
            "duration": e.get("duration"),
            "upload_date": e.get("upload_date", ""),
        })
    return videos


def duration_str(seconds) -> str:
    if not seconds:
        return "?"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}h{m:02d}m" if h else f"{m}m{s:02d}s"


def save_videos_md(author_dir: Path, author: dict, videos: list[dict]) -> None:
    lines = [
        f"# {author['name']} — Vídeos do Canal",
        "",
        f"Canal: {author['youtube_channel']}  ",
        f"Total de vídeos: {len(videos)}",
        "",
        "---",
        "",
    ]
    for v in videos:
        date = v["upload_date"]
        date_fmt = f"{date[:4]}-{date[4:6]}-{date[6:]}" if len(date) == 8 else date
        lines += [
            f"## {v['title']}",
            "",
            f"- **URL:** {v['url']}",
            f"- **Data:** {date_fmt}",
            f"- **Duração:** {duration_str(v['duration'])}",
        ]
        if v["description"]:
            lines += ["", v["description"]]
        lines += ["", "---", ""]

    out = author_dir / "videos.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    console.print(f"  [green]✓[/green] {out.relative_to(ROOT)}")


# ---------------------------------------------------------------------------
# 2. Extração de tópicos
# ---------------------------------------------------------------------------

def extract_topics(videos: list[dict], keywords_map: dict) -> dict[str, list[str]]:
    topics: dict[str, list[str]] = {topic: [] for topic in keywords_map}

    for v in videos:
        text = (v["title"] + " " + v["description"]).lower()
        for topic, keywords in keywords_map.items():
            if any(kw in text for kw in keywords):
                topics[topic].append(v["title"])

    return {k: v for k, v in topics.items() if v}


def save_topics_md(author_dir: Path, author: dict, topics: dict[str, list[str]]) -> None:
    lines = [
        f"# {author['name']} — Tópicos Identificados",
        "",
        f"> Extraído automaticamente de {sum(len(v) for v in topics.values())} vídeos.",
        "",
    ]
    for topic, titles in sorted(topics.items(), key=lambda x: -len(x[1])):
        lines += [f"## {topic} ({len(titles)} vídeos)", ""]
        for t in titles[:20]:
            lines.append(f"- {t}")
        if len(titles) > 20:
            lines.append(f"- _(e mais {len(titles) - 20} vídeos)_")
        lines.append("")

    out = author_dir / "topics.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    console.print(f"  [green]✓[/green] {out.relative_to(ROOT)}")


# ---------------------------------------------------------------------------
# 3. Summary por autor
# ---------------------------------------------------------------------------

def save_summary_md(author_dir: Path, author: dict, videos: list[dict], topics: dict[str, list[str]]) -> None:
    top_topics = sorted(topics.items(), key=lambda x: -len(x[1]))[:5]
    total_duration = sum(v["duration"] or 0 for v in videos)
    hours = total_duration // 3600

    lines = [
        f"# {author['name']} — Resumo",
        "",
        f"**Site:** {author['website']}  ",
        f"**Canal:** {author['youtube_channel']}  ",
        f"**Total de vídeos:** {len(videos)}  ",
        f"**Horas de conteúdo estimadas:** ~{hours}h",
        "",
        "## Especialidades declaradas",
        "",
    ]
    for s in author["specialties"]:
        lines.append(f"- {s}")

    lines += [
        "",
        "## Tópicos mais frequentes (extraídos automaticamente)",
        "",
    ]
    for topic, titles in top_topics:
        lines.append(f"- **{topic}** — {len(titles)} vídeos")

    out = author_dir / "summary.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    console.print(f"  [green]✓[/green] {out.relative_to(ROOT)}")


# ---------------------------------------------------------------------------
# 4. Transcrição via Whisper
# ---------------------------------------------------------------------------

def transcribe_video(video: dict, author_dir: Path, max_duration: int, verbose: bool) -> None:
    duration = video.get("duration") or 0
    if max_duration and duration > max_duration:
        if verbose:
            console.print(f"  [yellow]Pulando (duração {duration_str(duration)} > limite)[/yellow] {video['title'][:60]}")
        return

    slug = slugify(video["title"])
    out_md = author_dir / "transcripts" / f"{slug}.md"
    if out_md.exists():
        if verbose:
            console.print(f"  [dim]Já existe: {out_md.name}[/dim]")
        return

    audio_path = author_dir / "transcripts" / f"{slug}.mp3"

    # Baixar áudio
    dl_cmd = [
        "yt-dlp",
        "-x", "--audio-format", "mp3",
        "--audio-quality", "5",
        "-o", str(audio_path),
        "--no-warnings",
        video["url"],
    ]
    result = subprocess.run(dl_cmd, capture_output=True, text=True)
    if result.returncode != 0 or not audio_path.exists():
        console.print(f"  [red]Falha ao baixar áudio:[/red] {video['title'][:60]}")
        return

    # Transcrever
    try:
        import whisper  # type: ignore
        model = whisper.load_model("base")
        result_w = model.transcribe(str(audio_path), language="pt", fp16=False)
        transcript_text = result_w["text"].strip()
    except Exception as e:
        console.print(f"  [red]Falha na transcrição:[/red] {e}")
        audio_path.unlink(missing_ok=True)
        return

    # Salvar
    md_lines = [
        f"# Transcrição: {video['title']}",
        "",
        f"- **URL:** {video['url']}",
        f"- **Duração:** {duration_str(duration)}",
        "",
        "---",
        "",
        transcript_text,
    ]
    out_md.write_text("\n".join(md_lines), encoding="utf-8")
    audio_path.unlink(missing_ok=True)
    console.print(f"  [green]✓[/green] transcripts/{out_md.name}")


# ---------------------------------------------------------------------------
# 5. Índice geral
# ---------------------------------------------------------------------------

def save_index_md(sources: dict, all_topics: dict[str, dict[str, list[str]]]) -> None:
    all_topic_names = sorted({t for topics in all_topics.values() for t in topics})
    lines = [
        "# Knowledge Base — Índice Geral",
        "",
        "Gerado automaticamente por `tools/collect.py`.",
        "",
        "## Autores",
        "",
    ]
    for author in sources["authors"]:
        lines.append(f"- [{author['name']}]({author['id']}/summary.md)")
    lines.append("")

    lines += ["## Tópicos × Autores", ""]
    table_header = "| Tópico |" + "".join(f" {a['name'].split()[0]} |" for a in sources["authors"])
    table_sep = "|--------|" + "--------|" * len(sources["authors"])
    lines += [table_header, table_sep]

    for topic in all_topic_names:
        row = f"| {topic} |"
        for author in sources["authors"]:
            count = len(all_topics.get(author["id"], {}).get(topic, []))
            row += f" {count if count else '-'} |"
        lines.append(row)

    out = KNOWLEDGE_BASE / "_index.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    console.print(f"\n[green]✓[/green] {out.relative_to(ROOT)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def process_author(author: dict, sources: dict, args: argparse.Namespace) -> dict[str, list[str]]:
    console.rule(f"[bold cyan]{author['name']}[/bold cyan]")
    author_dir = ensure_dirs(author["id"])

    videos_file = author_dir / "videos.md"
    videos: list[dict] = []

    if videos_file.exists() and not args.force:
        console.print(f"  [dim]videos.md já existe — pulando coleta (use --force para reprocessar)[/dim]")
        # Tentar ler cache simples (sem reparsear o MD — reroda yt-dlp seria melhor)
        # Para simplicidade, recoletar mesmo assim se --transcribe precisar dos dados
        if args.transcribe:
            console.print("  [dim]Recoletando metadados para transcrição...[/dim]")
        else:
            # Sem transcrição não precisamos dos dados em memória — pula
            return {}

    if not videos or not videos_file.exists() or args.force:
        console.print(f"  Coletando metadados do canal...")
        videos = fetch_videos(author["youtube_channel"], verbose=args.verbose)
        console.print(f"  Encontrados [bold]{len(videos)}[/bold] vídeos")

        if not videos:
            console.print(f"  [yellow]Nenhum vídeo encontrado — verifique a URL do canal[/yellow]")
            return {}

        save_videos_md(author_dir, author, videos)
        time.sleep(2)

    topics = extract_topics(videos, sources["topics_keywords"])
    save_topics_md(author_dir, author, topics)
    save_summary_md(author_dir, author, videos, topics)

    if args.transcribe:
        console.print(f"\n  Iniciando transcrições ({len(videos)} vídeos)...")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Transcrevendo...", total=len(videos))
            for video in videos:
                progress.update(task, description=f"[cyan]{video['title'][:50]}[/cyan]")
                transcribe_video(video, author_dir, args.max_duration, args.verbose)
                progress.advance(task)
                time.sleep(1)

    return topics


def main() -> None:
    parser = argparse.ArgumentParser(description="Coleta knowledge base dos canais QA brasileiros")
    parser.add_argument("--author", help="ID do autor (ex: julio-de-lima). Padrão: todos")
    parser.add_argument("--transcribe", action="store_true", help="Ativar transcrição com Whisper")
    parser.add_argument("--force", action="store_true", help="Reprocessar mesmo se arquivos já existem")
    parser.add_argument("--max-duration", type=int, default=0, metavar="SEGUNDOS",
                        help="Ignorar vídeos mais longos que N segundos (ex: 3600 = 1h)")
    parser.add_argument("--verbose", action="store_true", help="Logs detalhados")
    args = parser.parse_args()

    sources = load_sources()
    authors = sources["authors"]

    if args.author:
        authors = [a for a in authors if a["id"] == args.author]
        if not authors:
            ids = [a["id"] for a in sources["authors"]]
            console.print(f"[red]Autor '{args.author}' não encontrado.[/red] IDs válidos: {ids}")
            sys.exit(1)

    console.print(f"\n[bold]qa-agents / collect.py[/bold]")
    console.print(f"Autores: {', '.join(a['id'] for a in authors)}")
    console.print(f"Transcrição: {'[green]sim[/green]' if args.transcribe else '[dim]não[/dim]'}\n")

    all_topics: dict[str, dict[str, list[str]]] = {}
    for author in authors:
        topics = process_author(author, sources, args)
        all_topics[author["id"]] = topics
        time.sleep(2)

    if not args.author:
        save_index_md(sources, all_topics)

    console.print("\n[bold green]Concluído![/bold green]")


if __name__ == "__main__":
    main()
