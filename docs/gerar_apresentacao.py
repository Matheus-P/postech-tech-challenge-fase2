#!/usr/bin/env python3
"""Gera docs/apresentacao_executiva.pdf a partir de results/metrics/.

Uso (depois de rodar os quatro notebooks):
    python docs/gerar_apresentacao.py

Todos os números dos slides são lidos dos arquivos gravados pelos notebooks,
de modo que a apresentação nunca diverge dos resultados.
"""

from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import JANELA_MESES, METRICS  # noqa: E402

SAIDA = ROOT / "docs" / "apresentacao_executiva.pdf"
RODAPE = "Grupo 30 · Turma 2DTATBB · POSTECH Data Analytics · Tech Challenge Fase 2"

FUNDO, CARTAO = "#fcfcfb", "#f3f2ee"
TINTA, TINTA_2, MUDO, GRADE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
AZUL, AZUL_ESCURO, AZUL_CLARO, LARANJA = "#2a78d6", "#0d366b", "#9ec5f4", "#eb6834"
L, A = 13.333, 7.5          # 16:9


# ------------------------------------------------------------------ dados --
def br(x: float, casas: int = 0) -> str:
    """Número no formato brasileiro: 1.234,5"""
    return f"{x:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x: float, casas: int = 1) -> str:
    return br(x * 100, casas) + "%"


def carregar() -> dict:
    eda = json.loads((METRICS / "resumo_eda.json").read_text())
    final = json.loads((METRICS / "modelo_final.json").read_text())
    hist = pd.read_csv(METRICS / "taxa_por_historico.csv", index_col=[0, 1])
    ablacao = pd.read_csv(METRICS / "ablacao_features.csv", index_col=0)
    teste = pd.read_csv(METRICS / "metricas_teste.csv", index_col=0)
    faixas = pd.read_csv(METRICS / "faixas_risco.csv", index_col=0)
    seg = pd.read_csv(METRICS / "segmentos.csv", index_col=0)
    audit = pd.read_csv(METRICS / "auditoria_vazamento.csv", index_col=0)

    cliente = hist.loc["Já era cliente?"]
    atraso = hist.loc["Atraso de 60+ dias em conta anterior?"]
    contas = int(cliente["contas"].sum())
    maus = round(float((cliente["contas"] * cliente["taxa_maus"]).sum()))
    corte = teste.iloc[1]
    return {
        "eda": eda, "final": final, "ablacao": ablacao[final["modelo"]], "faixas": faixas,
        "contas": contas, "maus": maus, "taxa": maus / contas,
        "taxa_primeira": cliente.loc["Primeira conta", "taxa_maus"],
        "taxa_cliente": cliente.loc["Já tinha conta", "taxa_maus"],
        "pct_cliente": cliente.loc["Já tinha conta", "contas"] / contas,
        "taxa_sem_atraso": atraso.loc["Não", "taxa_maus"],
        "taxa_com_atraso": atraso.loc["Sim", "taxa_maus"],
        "n_com_atraso": int(atraso.loc["Sim", "contas"]),
        "auc_teste": teste["roc_auc"].iloc[0],
        "precisao_corte": corte["precision"], "recall_corte": corte["recall"],
        "auc_cliente": seg["roc_auc"].iloc[0], "auc_primeira": seg["roc_auc"].iloc[1],
        "maus_teste": int(seg["maus"].sum()), "contas_teste": int(seg["contas"].sum()),
        "auc_aleatorio": audit["ROC-AUC médio"].iloc[0], "auc_agrupado": audit["ROC-AUC médio"].iloc[1],
    }


# ---------------------------------------------------------------- desenho --
def novo_slide(titulo: str, numero: int, subtitulo: str | None = None):
    fig = plt.figure(figsize=(L, A), facecolor=FUNDO)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, L)
    ax.set_ylim(0, A)
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0.7, 6.72), 0.5, 0.07, color=AZUL))
    ax.text(0.7, 6.5, "\n".join(textwrap.wrap(titulo, 54)), fontsize=27, fontweight="bold",
            color=TINTA, va="top", linespacing=1.15)
    if subtitulo:
        linhas = len(textwrap.wrap(titulo, 54))
        ax.text(0.7, 6.5 - 0.58 * linhas - 0.12, subtitulo, fontsize=14, color=TINTA_2, va="top")
    ax.text(0.7, 0.35, RODAPE, fontsize=9, color=MUDO)
    ax.text(L - 0.7, 0.35, str(numero), fontsize=9, color=MUDO, ha="right")
    return fig, ax


def cartao(ax, x, y, w, h, cor=CARTAO):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.12",
                                facecolor=cor, edgecolor="none"))


def numero_destaque(ax, x, y, w, valor, legenda, cor=AZUL, h=2.5):
    cartao(ax, x, y, w, h)
    ax.text(x + 0.35, y + h - 0.45, valor, fontsize=40, fontweight="bold", color=cor, va="top")
    ax.text(x + 0.35, y + h - 1.45, "\n".join(textwrap.wrap(legenda, int(w * 8.2))), fontsize=13.5,
            color=TINTA_2, va="top", linespacing=1.35)


def paragrafo(ax, x, y, texto, largura=60, tamanho=15, cor=TINTA_2, negrito=False):
    ax.text(x, y, "\n".join(textwrap.wrap(texto, largura)), fontsize=tamanho, color=cor, va="top",
            linespacing=1.4, fontweight="bold" if negrito else "normal")


def topicos(ax, x, y, itens, largura=58, tamanho=15, passo=0.38):
    for item in itens:
        linhas = textwrap.wrap(item, largura)
        ax.add_patch(plt.Circle((x + 0.07, y - 0.14), 0.055, color=AZUL))
        ax.text(x + 0.32, y, "\n".join(linhas), fontsize=tamanho, color=TINTA_2, va="top", linespacing=1.4)
        y -= passo * len(linhas) + 0.28
    return y


def eixo_grafico(fig, caixa):
    g = fig.add_axes(caixa, facecolor=FUNDO)
    for lado in ("top", "right", "left"):
        g.spines[lado].set_visible(False)
    g.spines["bottom"].set_color("#c3c2b7")
    g.tick_params(colors=TINTA_2, labelsize=12.5, length=0)
    g.yaxis.set_visible(False)
    return g


# ----------------------------------------------------------------- slides --
def slide_capa(d, n):
    fig = plt.figure(figsize=(L, A), facecolor=FUNDO)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, L)
    ax.set_ylim(0, A)
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 0.28, A, color=AZUL))
    ax.text(1.1, 5.55, "Tech Challenge · Fase 2", fontsize=15, color=AZUL, fontweight="bold")
    ax.text(1.1, 5.1, "Aprovar cartões de crédito\ncom menos inadimplência", fontsize=42, fontweight="bold",
            color=TINTA, va="top", linespacing=1.15)
    ax.text(1.1, 3.05, "Como o histórico de pagamento do próprio cliente\nantecipa o risco de um novo cartão",
            fontsize=19, color=TINTA_2, va="top", linespacing=1.4)
    ax.text(1.1, 1.05, "Grupo 30 · Turma 2DTATBB", fontsize=14, color=TINTA, fontweight="bold")
    ax.text(1.1, 0.68, "POSTECH Data Analytics", fontsize=13, color=MUDO)
    return fig


def slide_desafio(d, n):
    fig, ax = novo_slide("O desafio: aprovar bons clientes sem aprovar o prejuízo", n)
    numero_destaque(ax, 0.7, 2.75, 3.75, br(d["contas"]),
                    f"contas de cartão acompanhadas por {JANELA_MESES} meses após a abertura")
    numero_destaque(ax, 4.79, 2.75, 3.75, pct(d["taxa"]),
                    f"atrasaram 60 dias ou mais nesse período ({br(d['maus'])} contas)", cor=LARANJA)
    numero_destaque(ax, 8.88, 2.75, 3.75, pct(1 - d["taxa"]),
                    "é o acerto de quem aprova todo mundo, sem evitar um único calote", cor=TINTA_2)
    paragrafo(ax, 0.7, 2.2,
              "Maus pagadores são raros, mas cada um custa caro. Como são raros, medir o modelo pela taxa de "
              "acerto geral engana: o que importa é a capacidade de colocar os maus pagadores no topo da lista de risco.",
              largura=112, tamanho=15)
    return fig


def slide_achados(d, n):
    e = d["eda"]
    fig, ax = novo_slide("Antes de modelar, dois achados mudaram a análise", n)
    for x, titulo, valor, texto in [
        (0.7, "A mesma pessoa aparece várias vezes",
         f"{br(e['contas'])} contas, {br(e['proponentes'])} pessoas",
         f"{pct(e['pct_proponentes_com_mais_de_uma_conta'], 0)} dos clientes têm mais de um cartão. Se a mesma pessoa "
         f"entra no treino e no teste, o modelo parece melhor do que é: a nota caía de {br(d['auc_aleatorio'], 2)} "
         f"para {br(d['auc_agrupado'], 2)} quando separamos as pessoas. Todo resultado aqui usa essa separação."),
        (6.9, "Contas antigas pareciam piores",
         f"{pct(e['pct_atrasos_ate_12_meses'], 0)} dos atrasos graves\nem até 12 meses",
         "Quanto mais tempo uma conta é observada, mais chance de registrar um atraso. Para comparar todas na mesma "
         f"régua, o alvo passou a ser: atraso de 60 dias ou mais nos primeiros {JANELA_MESES} meses de conta."),
    ]:
        cartao(ax, x, 1.35, 5.75, 4.2)
        ax.text(x + 0.4, 5.15, titulo, fontsize=17, fontweight="bold", color=TINTA, va="top")
        linhas_valor = [l for parte in valor.split("\n") for l in textwrap.wrap(parte, 28)]
        ax.text(x + 0.4, 4.55, "\n".join(linhas_valor), fontsize=21, fontweight="bold", color=AZUL, va="top",
                linespacing=1.25)
        paragrafo(ax, x + 0.4, 3.8 - 0.45 * (len(linhas_valor) - 1), texto, largura=43, tamanho=15)
    return fig


def slide_ablacao(d, n):
    a = d["ablacao"]
    fig, ax = novo_slide("O formulário diz pouco; o histórico diz muito", n,
                         "Capacidade de separar bons e maus pagadores (0,5 = sorteio · 1,0 = perfeito)")
    g = eixo_grafico(fig, [0.06, 0.16, 0.5, 0.5])
    rotulos = ["Só o formulário\nde solicitação", "Só o histórico\nde pagamento", "Formulário\n+ histórico"]
    cores = [AZUL_CLARO, AZUL, AZUL_ESCURO]
    g.bar(rotulos, a.values - 0.5, bottom=0.5, color=cores, width=0.58)
    for i, v in enumerate(a.values):
        g.text(i, v + 0.008, br(v, 2), ha="center", fontsize=20, fontweight="bold", color=TINTA)
    g.set_ylim(0.5, 0.84)
    topicos(ax, 7.6, 5.0, [
        "Renda, idade, profissão e estado civil quase não distinguem quem vai atrasar.",
        "O que distingue é como a pessoa pagou os cartões que já tinha conosco.",
        "Usamos apenas o que o banco já sabe no dia do pedido: nada do futuro entra na conta.",
    ], largura=40)
    return fig


def slide_sinal(d, n):
    vezes = d["taxa_com_atraso"] / d["taxa_sem_atraso"]
    fig, ax = novo_slide(f"Quem já atrasou 60 dias volta a atrasar {br(vezes, 0)} vezes mais", n,
                         f"Contas com atraso grave nos primeiros {JANELA_MESES} meses, conforme o passado do cliente")
    g = eixo_grafico(fig, [0.06, 0.16, 0.42, 0.5])
    valores = [d["taxa_sem_atraso"] * 100, d["taxa_com_atraso"] * 100]
    g.bar(["Nunca atrasou 60 dias\nem cartões anteriores", "Já atrasou 60 dias\nem cartão anterior"], valores,
          color=[AZUL_CLARO, LARANJA], width=0.55)
    for i, v in enumerate(valores):
        g.text(i, v + 0.4, br(v, 1) + "%", ha="center", fontsize=22, fontweight="bold", color=TINTA)
    g.set_ylim(0, max(valores) * 1.2)
    topicos(ax, 6.9, 5.0, [
        f"É o sinal mais forte do modelo. São poucos casos ({br(d['n_com_atraso'])} contas), mas de risco muito alto.",
        f"Cliente novo é mais arriscado que cliente antigo: {pct(d['taxa_primeira'])} contra {pct(d['taxa_cliente'])} "
        "de atraso grave.",
        "Tempo de relacionamento e tempo no emprego atual reduzem o risco.",
    ], largura=46)
    return fig


def slide_resultado(d, n):
    f = d["faixas"]
    topo = f.iloc[-1]
    fig, ax = novo_slide(
        f"20% das contas concentram {pct(topo['%_dos_maus'], 0)} dos maus pagadores", n,
        f"Teste com {br(d['contas_teste'])} contas de clientes que o modelo nunca viu · taxa de atraso grave por faixa")
    g = eixo_grafico(fig, [0.06, 0.16, 0.52, 0.5])
    valores = f["taxa_maus"].values * 100
    cores = [AZUL_CLARO] * 3 + [AZUL, AZUL_ESCURO]
    g.bar(["Faixa 1\nmenor risco", "Faixa 2", "Faixa 3", "Faixa 4", "Faixa 5\nmaior risco"], valores,
          color=cores, width=0.62)
    for i, v in enumerate(valores):
        g.text(i, v + 0.1, br(v, 1) + "%", ha="center", fontsize=18, fontweight="bold", color=TINTA)
    media = f["maus"].sum() / f["contas"].sum() * 100
    g.axhline(media, color=MUDO, linewidth=1, linestyle="--")
    g.text(-0.42, media + 0.08, f"média {br(media, 1)}%", fontsize=10.5, color=MUDO)
    g.set_ylim(0, max(valores) * 1.2)
    baixo = f.iloc[:3]
    topicos(ax, 7.9, 5.0, [
        f"Na faixa 5, o atraso grave é {br(topo['taxa_maus'] * 100 / media, 1)} vezes a média da carteira.",
        f"As três faixas mais seguras somam 60% das contas, com {pct(baixo['maus'].sum() / baixo['contas'].sum())} de atraso grave.",
        f"Nota de separação no teste: {br(d['auc_teste'], 2)} (0,5 = sorteio).",
    ], largura=38)
    return fig


def slide_politica(d, n):
    f = d["faixas"]
    baixo = f.iloc[:3]
    um_em = 1 / d["precisao_corte"]
    fig, ax = novo_slide("Como usar: três tratamentos em vez de um sim ou não", n)
    blocos = [
        ("Faixas 1 a 3", "60% dos pedidos", AZUL_CLARO, "Aprovação automática",
         f"Atraso grave de {pct(baixo['maus'].sum() / baixo['contas'].sum())}. Aprovar sem atrito: é aqui que está o "
         "crescimento saudável da carteira."),
        ("Faixa 4", "20% dos pedidos", AZUL, "Aprovação com limite inicial menor",
         f"Atraso grave de {pct(f.iloc[3]['taxa_maus'])}, próximo da média. Começar com limite reduzido e aumentar "
         "conforme o cliente paga em dia."),
        ("Faixa 5", "20% dos pedidos", AZUL_ESCURO, "Análise reforçada",
         f"Atraso grave de {pct(f.iloc[4]['taxa_maus'])}. Revisão manual ou exigência de garantia. Nos pedidos "
         f"de pontuação mais alta, 1 em cada {br(um_em, 0)} atrasa."),
    ]
    for i, (faixa, volume, cor, acao, texto) in enumerate(blocos):
        x = 0.7 + i * 4.09
        cartao(ax, x, 1.3, 3.75, 4.2)
        ax.add_patch(FancyBboxPatch((x, 5.38), 3.75, 0.12, boxstyle="round,pad=0,rounding_size=0.05",
                                    facecolor=cor, edgecolor="none"))
        ax.text(x + 0.35, 5.05, faixa, fontsize=20, fontweight="bold", color=TINTA, va="top")
        ax.text(x + 0.35, 4.52, volume, fontsize=13, color=MUDO, va="top")
        paragrafo(ax, x + 0.35, 3.95, acao, largura=26, tamanho=16, cor=TINTA, negrito=True)
        paragrafo(ax, x + 0.35, 3.05, texto, largura=31, tamanho=14)
    return fig


def slide_limites(d, n):
    fig, ax = novo_slide("O que o modelo ainda não resolve, e os próximos passos", n)
    cartao(ax, 0.7, 1.3, 5.75, 4.2)
    ax.text(1.1, 5.1, "Limites", fontsize=18, fontweight="bold", color=TINTA, va="top")
    topicos(ax, 1.1, 4.45, [
        f"Para quem pede o primeiro cartão não há histórico: a separação cai de {br(d['auc_cliente'], 2)} para "
        f"{br(d['auc_primeira'], 2)}, perto do sorteio.",
        f"Maus pagadores são poucos ({br(d['maus_teste'])} no teste), então os números têm margem de erro.",
        "Tratamos cadastros idênticos como a mesma pessoa; a base não traz um identificador de cliente.",
    ], largura=42, tamanho=14.5, passo=0.36)
    cartao(ax, 6.9, 1.3, 5.75, 4.2)
    ax.text(7.3, 5.1, "Próximos passos", fontsize=18, fontweight="bold", color=TINTA, va="top")
    topicos(ax, 7.3, 4.45, [
        "Trazer dados de bureau de crédito para avaliar quem ainda não é cliente.",
        "Rodar em piloto ao lado da política atual e medir a inadimplência por faixa.",
        "Acompanhar mês a mês se o perfil dos pedidos e os resultados se mantêm.",
    ], largura=42, tamanho=14.5, passo=0.36)
    return fig


def main() -> None:
    d = carregar()
    # Registra as fontes que vêm com o matplotlib: o PDF não depende do cache de fontes da máquina.
    for fonte in font_manager.findSystemFonts(str(Path(matplotlib.get_data_path()) / "fonts" / "ttf")):
        font_manager.fontManager.addfont(fonte)
    plt.rcParams["font.family"] = "DejaVu Sans"
    slides = [slide_capa, slide_desafio, slide_achados, slide_ablacao, slide_sinal,
              slide_resultado, slide_politica, slide_limites]
    with PdfPages(SAIDA, metadata={"Title": "Aprovar cartões de crédito com menos inadimplência",
                                   "Author": "Grupo 30 - 2DTATBB", "CreationDate": None}) as pdf:
        for n, slide in enumerate(slides, start=1):
            fig = slide(d, n)
            pdf.savefig(fig, facecolor=FUNDO)
            plt.close(fig)
    print(f"{len(slides)} slides -> {SAIDA.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
