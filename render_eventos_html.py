"""
Renderiza os eventos do Appai como HTML rico (nao markdown generico) -
cores por categoria, cards com titulo/elegibilidade, e botoes de acao
(Mais informacoes / Inscrever-se). Le direto dos snapshots/*.json.

Compartilhado entre apresentar_resumo.py (boletim local) e
gerar_pagina_web.py (pagina publica no GitHub Pages).
"""
import json
from pathlib import Path

PASTA_APPAI = Path(__file__).parent
SNAPSHOTS_DIR = PASTA_APPAI / "snapshots"

CORES_CATEGORIA = {
    "agito": "#7c3aed",
    "bom-espetaculo": "#dc2626",
    "caminhadas-e-corridas": "#16a34a",
    "passeio-cultural": "#0891b2",
}

NOMES_EXIBICAO = {
    "agito": "Agitô",
    "bom-espetaculo": "Bom Espetáculo",
    "caminhadas-e-corridas": "Caminhadas e Corridas",
    "passeio-cultural": "Passeio Cultural",
}

BOTAO_CSS = (
    "display:inline-block;background:#f97316;color:#ffffff;"
    "font-weight:bold;text-decoration:none;padding:8px 16px;"
    "border-radius:8px;margin:4px 8px 4px 0;font-size:0.9rem;"
)


def _escapar(texto):
    if not texto:
        return ""
    return (
        texto.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _card_evento(event):
    titulo = _escapar(event.get("title", "(sem titulo)"))
    tag = _escapar(event.get("tag") or "")

    linhas = ['<div class="evento-card">']
    linhas.append(f'<div class="evento-titulo">{titulo}</div>')
    if tag:
        linhas.append(f'<div class="evento-tag">{tag}</div>')

    if event.get("elegivel") is False:
        motivo = _escapar(event.get("motivo_bloqueio") or "")
        linhas.append(f'<div class="evento-bloqueado">⛔ Bloqueado: {motivo}</div>')
    elif event.get("elegivel") is True:
        linhas.append('<div class="evento-elegivel">✅ Você está elegível pra se inscrever</div>')

    if event.get("requires_donation"):
        qty = _escapar(event.get("donation_quantity") or "quantidade não especificada")
        linhas.append(f'<div class="evento-doacao">Doação exigida: {qty}</div>')

    for r in event.get("rewards", []) or []:
        linhas.append(f'<div class="evento-premio">🎁 {_escapar(r)}</div>')

    botoes = []
    if event.get("pagina_publica_url"):
        botoes.append(
            f'<a href="{_escapar(event["pagina_publica_url"])}" target="_blank" '
            f'style="{BOTAO_CSS}">Mais informações</a>'
        )
    if event.get("registration_url"):
        botoes.append(
            f'<a href="{_escapar(event["registration_url"])}" target="_blank" '
            f'style="{BOTAO_CSS}">Inscrever-se</a>'
        )
    if botoes:
        linhas.append('<div class="evento-botoes">' + "".join(botoes) + '</div>')

    linhas.append('</div>')
    return "\n".join(linhas)


def gerar_html_eventos_completos():
    blocos = []
    ordem = ["agito", "bom-espetaculo", "caminhadas-e-corridas", "passeio-cultural"]

    for page_name in ordem:
        snap_path = SNAPSHOTS_DIR / f"{page_name}.json"
        if not snap_path.exists():
            continue
        snap = json.loads(snap_path.read_text(encoding="utf-8"))
        events = snap.get("events") or []
        if not events:
            continue

        cor = CORES_CATEGORIA.get(page_name, "#326c99")
        nome_exibicao = NOMES_EXIBICAO.get(page_name, page_name)
        atualizado_em = (snap.get("checked_at") or "")[:16].replace("T", " ")
        cards_html = "\n".join(_card_evento(e) for e in events)

        blocos.append(
            f'<details class="categoria-appai">'
            f'<summary style="color:{cor};font-weight:bold;">'
            f'{nome_exibicao} ({len(events)} evento(s) - atualizado em {atualizado_em})'
            f'</summary>'
            f'<div class="categoria-conteudo">{cards_html}</div>'
            f'</details>'
        )

    if not blocos:
        return ""

    estilo = """
    <style>
      .categoria-appai { margin: 10px 0; border: 1px solid #d9e2ef; border-radius: 14px; padding: 10px 16px; background: #fafcff; }
      .categoria-appai summary { cursor: pointer; font-size: 1.05rem; padding: 4px 0; }
      .categoria-conteudo { padding: 8px 0; }
      .evento-card { border-bottom: 1px solid #e2eaf2; padding: 12px 0; }
      .evento-card:last-child { border-bottom: none; }
      .evento-titulo { font-weight: 600; font-size: 1rem; color: #1e2b3a; }
      .evento-tag { font-size: 0.85rem; color: #5e6f82; margin-top: 2px; }
      .evento-bloqueado { color: #b91c1c; font-size: 0.9rem; margin-top: 6px; }
      .evento-elegivel { color: #15803d; font-size: 0.9rem; margin-top: 6px; }
      .evento-doacao, .evento-premio { font-size: 0.9rem; color: #5e6f82; margin-top: 4px; }
      .evento-botoes { margin-top: 10px; }
    </style>
    """
    return estilo + "\n".join(blocos)
