# PROMPT PARA O CLAUDE DO VSCODE
# Cole isso inteiro no chat do Claude Code dentro do VSCode

---

Você está trabalhando no projeto `qa-agents`, uma base de conhecimento e sistema
de agentes especializados em QA/Qualidade de Software.

## Contexto do projeto

A pasta `knowledge_base/` precisa ser populada com arquivos `.md` extraídos
do conteúdo público dos seguintes criadores brasileiros de QA:

### Fontes

| ID | Nome | Canal YouTube | Site |
|----|------|--------------|------|
| `julio-de-lima` | Júlio de Lima | https://www.youtube.com/@JuliodeLimas | https://juliodelima.com.br |
| `fernando-papito` | Fernando Papito | https://www.youtube.com/channel/UCzsGhfwdImeKj2AOoN92hFw | https://fernandopapito.com |
| `qazando` | QAzando | https://www.youtube.com/c/QAzando | https://qazando.com.br |
| `vinicius-pessoni` | Vinícius Pessoni | https://www.youtube.com/c/pessonizando | https://viniciuspessoni.com |

### Estrutura esperada de saída

```
knowledge_base/
  julio-de-lima/
    videos.md          ← lista de vídeos com título, URL, descrição
    transcripts/       ← transcrições por vídeo (quando disponível)
    topics.md          ← tópicos identificados nos vídeos
    summary.md         ← resumo da especialidade e pontos fortes
  fernando-papito/
    (mesma estrutura)
  qazando/
    (mesma estrutura)
  vinicius-pessoni/
    (mesma estrutura)
  _index.md            ← índice geral cruzando todos os temas
```

## Tarefa

Crie o script `tools/collect.py` com as seguintes funcionalidades:

### 1. Coleta de metadados do YouTube via yt-dlp
- Listar todos os vídeos de cada canal (título, URL, descrição, duração, data)
- Salvar em `knowledge_base/{autor}/videos.md`
- Usar apenas metadados (sem baixar vídeos)

### 2. Transcrição automática via yt-dlp + Whisper (opcional)
- Flag `--transcribe` para ativar transcrição
- Baixar apenas o áudio (formato mp3, menor tamanho)
- Transcrever com `openai-whisper` modelo `base` (rápido, suficiente para PT-BR)
- Salvar em `knowledge_base/{autor}/transcripts/{video-slug}.md`
- Deletar o áudio após transcrever (economizar espaço)

### 3. Extração de tópicos
- Após coletar metadados, analisar títulos e descrições
- Agrupar por tema: API, Mobile, Web, Performance, Carreira, DevOps, etc.
- Salvar em `knowledge_base/{autor}/topics.md`

### 4. Geração de summary por autor
- Com base nos tópicos encontrados, gerar `summary.md` com:
  - Especialidades principais
  - Ferramentas mais citadas
  - Stack predominante
  - Pontos fortes identificados

### 5. Índice geral
- Gerar `knowledge_base/_index.md` cruzando todos os autores por tema

## Requisitos técnicos

```python
# Dependências necessárias
# pip install yt-dlp openai-whisper tqdm rich

# Compatível com Python 3.9+
# Deve ter tratamento de erros e rate limiting (sleep entre requests)
# Logs claros com rich para acompanhar o progresso
# Arquivo de config: tools/sources.json com as URLs dos canais
```

## Exemplo de uso esperado

```bash
# Só metadados (rápido, ~2 min por canal)
python tools/collect.py

# Com transcrição (lento, ~5-10 min por vídeo)
python tools/collect.py --transcribe

# Só um autor específico
python tools/collect.py --author julio-de-lima

# Só um autor com transcrição
python tools/collect.py --author fernando-papito --transcribe

# Ver progresso detalhado
python tools/collect.py --verbose
```

## Arquivo de configuração

Crie também `tools/sources.json`:

```json
{
  "authors": [
    {
      "id": "julio-de-lima",
      "name": "Júlio de Lima",
      "youtube_channel": "https://www.youtube.com/@JuliodeLimas",
      "website": "https://juliodelima.com.br",
      "specialties": ["API REST", "BDD", "Cypress", "Playwright", "JMeter", "Estratégia de Testes"],
      "language": "pt-BR"
    },
    {
      "id": "fernando-papito",
      "name": "Fernando Papito",
      "youtube_channel": "https://www.youtube.com/channel/UCzsGhfwdImeKj2AOoN92hFw",
      "website": "https://fernandopapito.com",
      "specialties": ["Playwright", "Robot Framework", "DevOps", "CI/CD", "Arquitetura de Frameworks"],
      "language": "pt-BR"
    },
    {
      "id": "qazando",
      "name": "QAzando",
      "youtube_channel": "https://www.youtube.com/c/QAzando",
      "website": "https://qazando.com.br",
      "specialties": ["Automação Mobile", "Cypress", "Appium", "Gestão de Equipes QA"],
      "language": "pt-BR"
    },
    {
      "id": "vinicius-pessoni",
      "name": "Vinícius Pessoni",
      "youtube_channel": "https://www.youtube.com/c/pessonizando",
      "website": "https://viniciuspessoni.com",
      "specialties": ["RestAssured", "Java", "JUnit5", "CTFL", "Liderança", "Carreira Internacional"],
      "language": "pt-BR"
    }
  ],
  "topics_keywords": {
    "API": ["api", "rest", "restassured", "postman", "insomnia", "swagger", "endpoint", "http"],
    "Web": ["playwright", "cypress", "selenium", "browser", "e2e", "interface", "frontend"],
    "Mobile": ["mobile", "appium", "maestro", "android", "ios", "app"],
    "Performance": ["performance", "carga", "jmeter", "k6", "stress", "load"],
    "DevOps": ["devops", "ci", "cd", "pipeline", "github actions", "jenkins", "docker"],
    "Carreira": ["carreira", "salário", "mercado", "vaga", "emprego", "internacional"],
    "Fundamentos": ["fundamentos", "estratégia", "bdd", "tdd", "ctfl", "istqb", "qualidade"],
    "Robot Framework": ["robot", "robot framework", "keyword", "library"],
    "Java": ["java", "junit", "gradle", "maven", "restassured"],
    "IA": ["inteligência artificial", "ia", "ai", "machine learning", "copilot", "claude"]
  }
}
```

## Observações importantes

1. **Rate limiting**: adicionar `time.sleep(2)` entre requests ao YouTube para não ser bloqueado
2. **Idempotente**: se o arquivo já existe, não reprocessar (flag `--force` para forçar)
3. **Sem API key**: usar yt-dlp que não precisa de chave da YouTube API
4. **Transcrição PT-BR**: passar `language="pt"` no Whisper para melhor acurácia
5. **Tamanho**: vídeos longos (>1h) podem ser pesados — adicionar flag `--max-duration 3600`

Depois de criar o script, crie também um `tools/requirements.txt` com todas as dependências.
