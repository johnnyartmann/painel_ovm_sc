"""
Módulo para geração de relatório PDF pré-configurado.
Gera um documento PDF completo com todas as tabelas e gráficos do painel,
usando um layout fixo que funciona bem tanto em desktop quanto em dispositivo móvel.
"""

import io
import os
import tempfile
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.io as pio
from fpdf import FPDF

from tabs.analise_geral import (
    criar_tabela_consolidada,
    criar_tabela_total_consolidada,
    criar_tabela_populacional_agrupada,
)
from tabs.analise_feminicidios import (
    criar_tabela_feminicidio_agrupado,
    criar_tabela_total_feminicidio,
    calcular_indice_letalidade,
)
from plotting import (
    plot_serie_temporal,
    plot_dia_semana,
    plot_por_ano,
    plot_por_mes,
    plot_faixa_etaria,
    plot_tipo_crime,
    plot_barras_vulnerabilidade,
    plot_feminicidio_serie_temporal,
    plot_feminicidio_por_ano,
    plot_vinculo_autor,
    plot_meio_crime,
    plot_autor_preso,
    plot_bo_contra_autor,
)
from utils import calcular_tendencia_mensal


# ============================================================================
# CONSTANTES DE CORES E LAYOUT
# ============================================================================
ROXO_ESCURO = (74, 20, 140)       # #4a148c
ROXO_MEDIO = (142, 36, 170)       # #8e24aa
ROXO_CLARO = (171, 71, 188)       # #ab47bc
ROXO_BG = (245, 235, 250)         # fundo claro
BRANCO = (255, 255, 255)
CINZA_TEXTO = (60, 60, 60)
CINZA_CLARO = (240, 240, 240)
PRETO = (0, 0, 0)

MARGEM = 10
LARGURA_A4_LANDSCAPE = 297
ALTURA_A4_LANDSCAPE = 210


# ============================================================================
# CLASSE DO PDF
# ============================================================================
class RelatorioPDF(FPDF):
    """PDF personalizado com cabeçalho e rodapé automáticos."""

    def __init__(self, logo_path=None, periodo_texto=""):
        super().__init__(orientation='L', unit='mm', format='A4')
        self.logo_path = logo_path
        self.periodo_texto = periodo_texto
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        """Cabeçalho roxo em cada página."""
        if self.page_no() == 1:
            return  # A capa tem seu próprio layout

        # Barra roxa no topo
        self.set_fill_color(*ROXO_ESCURO)
        self.rect(0, 0, self.w, 14, 'F')

        # Logo pequeno
        if self.logo_path and os.path.exists(self.logo_path):
            self.image(self.logo_path, 5, 1.5, 11)

        # Título
        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(*BRANCO)
        self.set_xy(18, 2)
        self.cell(0, 5, 'Observatorio da Violencia Contra a Mulher - SC', align='L')

        # Período
        self.set_font('Helvetica', '', 7)
        self.set_xy(18, 7)
        self.cell(0, 5, self.periodo_texto, align='L')

        # Linha separadora
        self.set_draw_color(*ROXO_CLARO)
        self.set_line_width(0.5)
        self.line(0, 14, self.w, 14)

        self.set_y(18)

    def footer(self):
        """Rodapé com número de página."""
        if self.page_no() == 1:
            return

        self.set_y(-12)
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Página {self.page_no() - 1}', align='C')

        # Data de geração à direita
        self.set_y(-12)
        data_geracao = datetime.now().strftime('%d/%m/%Y as %H:%M')
        self.cell(0, 10, f'Gerado em {data_geracao}', align='R')


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================
def _fig_to_image(fig, width=900, height=450):
    """Converte uma figura Plotly em bytes PNG."""
    try:
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=11),
            margin=dict(l=50, r=30, t=40, b=50),
        )
        img_bytes = pio.to_image(fig, format='png', width=width, height=height, scale=2)
        return img_bytes
    except Exception:
        return None


def _add_image_to_pdf(pdf, img_bytes, w=260):
    """Adiciona uma imagem (bytes PNG) ao PDF."""
    if img_bytes is None:
        return

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        tmp.write(img_bytes)
        tmp_path = tmp.name

    try:
        # Calcular altura proporcional
        from PIL import Image as PILImage
        with PILImage.open(tmp_path) as img:
            img_w, img_h = img.size
        h = w * img_h / img_w

        # Verificar se cabe na página
        espaco_restante = pdf.h - pdf.get_y() - 20
        if h > espaco_restante:
            pdf.add_page()

        x = (pdf.w - w) / 2
        pdf.image(tmp_path, x=x, y=pdf.get_y(), w=w)
        pdf.set_y(pdf.get_y() + h + 5)
    except Exception:
        pass
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def _add_section_title(pdf, titulo):
    """Adiciona um título de seção estilizado."""
    espaco_restante = pdf.h - pdf.get_y() - 20
    if espaco_restante < 30:
        pdf.add_page()

    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(*ROXO_ESCURO)
    pdf.cell(0, 10, titulo, ln=True)

    # Linha decorativa roxa
    y = pdf.get_y()
    pdf.set_draw_color(*ROXO_MEDIO)
    pdf.set_line_width(0.8)
    pdf.line(MARGEM, y, 120, y)
    pdf.ln(4)


def _add_subsection_title(pdf, titulo):
    """Adiciona um subtítulo."""
    espaco_restante = pdf.h - pdf.get_y() - 20
    if espaco_restante < 25:
        pdf.add_page()

    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(*ROXO_MEDIO)
    pdf.cell(0, 8, titulo, ln=True)
    pdf.ln(2)


def _format_value(val):
    """Formata valor para exibição na tabela do PDF."""
    if pd.isna(val):
        return '-'
    if isinstance(val, float):
        if abs(val) > 1000:
            return f"{val:,.0f}".replace(",", ".")
        return f"{val:.2f}".replace(".", ",")
    if isinstance(val, (int, np.integer)):
        return f"{val:,}".replace(",", ".")
    return str(val)


def _add_dataframe_table(pdf, df, col_widths=None, title=None, max_rows=80):
    """Renderiza um DataFrame como tabela no PDF."""
    if df is None or df.empty:
        pdf.set_font('Helvetica', 'I', 9)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 8, 'Nenhum dado disponivel para exibir.', ln=True)
        return

    if title:
        _add_subsection_title(pdf, title)

    # Limitar linhas
    df_display = df.head(max_rows).copy()

    columns = list(df_display.columns)
    n_cols = len(columns)

    # Calcular larguras das colunas
    usable_w = pdf.w - 2 * MARGEM
    if col_widths is None:
        col_widths = [usable_w / n_cols] * n_cols

    # Ajustar se exceder largura disponível
    total_w = sum(col_widths)
    if total_w > usable_w:
        ratio = usable_w / total_w
        col_widths = [w * ratio for w in col_widths]

    row_height = 6
    font_size_header = 7
    font_size_body = 6.5

    # --- Cabeçalho da tabela ---
    pdf.set_font('Helvetica', 'B', font_size_header)
    pdf.set_fill_color(*ROXO_ESCURO)
    pdf.set_text_color(*BRANCO)

    x_start = MARGEM
    for i, col in enumerate(columns):
        col_name = str(col)
        # Truncar nomes longos
        if len(col_name) > 20:
            col_name = col_name[:18] + '..'
        pdf.set_xy(x_start + sum(col_widths[:i]), pdf.get_y())
        pdf.cell(col_widths[i], row_height + 1, col_name, border=1, align='C', fill=True)
    pdf.ln(row_height + 1)

    # --- Linhas de dados ---
    pdf.set_font('Helvetica', '', font_size_body)
    for idx, row in df_display.iterrows():
        # Verificar se cabe na página
        if pdf.get_y() + row_height > pdf.h - 20:
            pdf.add_page()
            # Re-renderizar cabeçalho da tabela na nova página
            pdf.set_font('Helvetica', 'B', font_size_header)
            pdf.set_fill_color(*ROXO_ESCURO)
            pdf.set_text_color(*BRANCO)
            for i, col in enumerate(columns):
                col_name = str(col)
                if len(col_name) > 20:
                    col_name = col_name[:18] + '..'
                pdf.set_xy(x_start + sum(col_widths[:i]), pdf.get_y())
                pdf.cell(col_widths[i], row_height + 1, col_name, border=1, align='C', fill=True)
            pdf.ln(row_height + 1)
            pdf.set_font('Helvetica', '', font_size_body)

        # Alternar cor de fundo
        is_even = (list(df_display.index).index(idx) % 2 == 0)
        if is_even:
            pdf.set_fill_color(*CINZA_CLARO)
        else:
            pdf.set_fill_color(*BRANCO)

        pdf.set_text_color(*CINZA_TEXTO)

        y_row = pdf.get_y()
        for i, col in enumerate(columns):
            val = row[col]
            formatted = _format_value(val)

            # Colorir colunas de evolução/tendência
            col_str = str(col)
            if 'Diferença' in col_str or 'Tendência' in col_str:
                try:
                    num_val = float(val) if not pd.isna(val) else 0
                    if num_val > 0:
                        pdf.set_text_color(220, 50, 50)  # vermelho
                    elif num_val < 0:
                        pdf.set_text_color(50, 150, 50)  # verde
                    else:
                        pdf.set_text_color(*CINZA_TEXTO)
                except (ValueError, TypeError):
                    pdf.set_text_color(*CINZA_TEXTO)

            # Alinhar: texto à esquerda, números à direita
            align = 'L' if i == 0 else 'R'
            if isinstance(val, str) and not any(c.isdigit() for c in val[:3] if val):
                align = 'L'

            pdf.set_xy(x_start + sum(col_widths[:i]), y_row)
            pdf.cell(col_widths[i], row_height, formatted, border=1, align=align, fill=True)

            pdf.set_text_color(*CINZA_TEXTO)

        pdf.ln(row_height)

    pdf.ln(5)

    # Nota se dados foram truncados
    if len(df) > max_rows:
        pdf.set_font('Helvetica', 'I', 7)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 5, f'* Exibindo as primeiras {max_rows} de {len(df)} linhas.', ln=True)

        pdf.ln(3)


def _add_kpi_cards(pdf, kpis):
    """Adiciona cards de KPI ao PDF. kpis = lista de dicts com 'label' e 'value'."""
    n = len(kpis)
    if n == 0:
        return

    card_w = min(65, (pdf.w - 2 * MARGEM - (n - 1) * 5) / n)
    card_h = 20
    x_start = (pdf.w - (card_w * n + 5 * (n - 1))) / 2
    y = pdf.get_y()

    # Verificar espaço
    if y + card_h + 5 > pdf.h - 20:
        pdf.add_page()
        y = pdf.get_y()

    for i, kpi in enumerate(kpis):
        x = x_start + i * (card_w + 5)

        # Fundo do card
        pdf.set_fill_color(*ROXO_BG)
        pdf.set_draw_color(*ROXO_CLARO)
        pdf.rect(x, y, card_w, card_h, 'DF')

        # Label
        pdf.set_font('Helvetica', '', 6.5)
        pdf.set_text_color(*ROXO_MEDIO)
        pdf.set_xy(x + 2, y + 2)
        pdf.cell(card_w - 4, 4, kpi['label'], align='C')

        # Valor
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(*ROXO_ESCURO)
        pdf.set_xy(x + 2, y + 7)
        pdf.cell(card_w - 4, 10, str(kpi['value']), align='C')

    pdf.set_y(y + card_h + 8)


# ============================================================================
# GERAÇÃO DO RELATÓRIO COMPLETO
# ============================================================================
def gerar_relatorio_pdf():
    """
    Gera o relatório PDF completo com todas as tabelas e gráficos das
    duas abas (Análise Geral + Análise de Feminicídios), usando os
    filtros atualmente aplicados no session_state.

    Returns:
        bytes: O conteúdo do PDF pronto para download.
    """
    import streamlit as st

    # --- Recuperar dados do session_state ---
    df_geral = st.session_state.get('df_geral_filtrado', pd.DataFrame())
    df_feminicidio = st.session_state.get('df_feminicidio_filtrado', pd.DataFrame())
    df_populacao = st.session_state.get('df_populacao', pd.DataFrame())
    df_regioes = st.session_state.get('df_regioes', pd.DataFrame())
    agrupamento = st.session_state.get('agrupamento_selecionado', 'Consolidado')
    data_inicial = st.session_state.get('data_inicial')
    data_final = st.session_state.get('data_final')

    # Texto do período
    if data_inicial and data_final:
        periodo_texto = f"Periodo: {data_inicial.strftime('%d/%m/%Y')} a {data_final.strftime('%d/%m/%Y')}"
    else:
        periodo_texto = "Periodo: Todos os dados disponiveis"

    # Logo
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logo_ovm.png')
    if not os.path.exists(logo_path):
        logo_path = None

    # --- Criar o PDF ---
    pdf = RelatorioPDF(logo_path=logo_path, periodo_texto=periodo_texto)
    pdf.add_page()

    # =====================================================================
    # CAPA (desabilitar auto page break para evitar páginas em branco)
    # =====================================================================
    pdf.set_auto_page_break(auto=False)

    # Fundo roxo na capa inteira
    pdf.set_fill_color(*ROXO_ESCURO)
    pdf.rect(0, 0, pdf.w, pdf.h, 'F')

    # Logo grande centralizado
    if logo_path:
        logo_w = 60
        logo_x = (pdf.w - logo_w) / 2
        pdf.image(logo_path, x=logo_x, y=35, w=logo_w)

    # Título principal
    pdf.set_font('Helvetica', 'B', 28)
    pdf.set_text_color(*BRANCO)
    pdf.set_y(105)
    pdf.cell(0, 15, 'Relatorio do Observatorio da', align='C', ln=True)
    pdf.cell(0, 15, 'Violencia Contra a Mulher', align='C', ln=True)

    # Subtítulo
    pdf.set_font('Helvetica', '', 16)
    pdf.set_text_color(200, 180, 220)
    pdf.ln(5)
    pdf.cell(0, 10, 'Santa Catarina', align='C', ln=True)

    # Linha decorativa
    pdf.ln(8)
    y_line = pdf.get_y()
    pdf.set_draw_color(*BRANCO)
    pdf.set_line_width(0.5)
    center_x = pdf.w / 2
    pdf.line(center_x - 60, y_line, center_x + 60, y_line)

    # Filtros aplicados
    pdf.ln(8)
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(*BRANCO)
    pdf.cell(0, 8, periodo_texto, align='C', ln=True)
    pdf.cell(0, 8, f'Agrupamento: {agrupamento}', align='C', ln=True)
    pdf.cell(0, 8, f'Total de registros (geral): {len(df_geral):,}'.replace(',', '.'), align='C', ln=True)
    pdf.cell(0, 8, f'Total de feminicidios: {len(df_feminicidio):,}'.replace(',', '.'), align='C', ln=True)

    # Data de geracao
    pdf.set_y(pdf.h - 25)
    pdf.set_font('Helvetica', 'I', 9)
    pdf.set_text_color(180, 160, 200)
    pdf.cell(0, 8, f'Relatorio gerado em {datetime.now().strftime("%d/%m/%Y as %H:%M")}', align='C')

    # Reabilitar auto page break para o restante do relatório
    pdf.set_auto_page_break(auto=True, margin=20)

    # =====================================================================
    # SECAO 1: RESUMO EXECUTIVO - ANALISE GERAL
    # =====================================================================
    pdf.add_page()
    _add_section_title(pdf, "Resumo Executivo -- Analise Geral")

    total_registros = len(df_geral)
    num_dias = (data_final - data_inicial).days + 1 if data_inicial and data_final else 1
    crimes_por_dia = total_registros / num_dias if num_dias > 0 else 0
    crimes_por_hora = total_registros / (num_dias * 24) if num_dias > 0 else 0

    media_idade = 0.0
    if not df_geral.empty and df_geral['idade_vitima'].notna().any():
        media_idade = df_geral['idade_vitima'].mean()

    pct_fds = 0
    if not df_geral.empty:
        ocorr_fds = df_geral[df_geral['data_fato'].dt.dayofweek.isin([5, 6])].shape[0]
        pct_fds = (ocorr_fds / total_registros * 100) if total_registros > 0 else 0

    tendencia = calcular_tendencia_mensal(df_geral)
    tend_texto = f"{tendencia:.1f}% a.a." if pd.notna(tendencia) else "N/A"

    _add_kpi_cards(pdf, [
        {'label': 'Total Registros', 'value': f"{total_registros:,}".replace(',', '.')},
        {'label': 'Media/Dia', 'value': f"{crimes_por_dia:.1f}"},
        {'label': 'Media/Hora', 'value': f"{crimes_por_hora:.2f}"},
        {'label': 'Tendencia', 'value': tend_texto},
        {'label': 'Idade Media Vitima', 'value': f"{media_idade:.1f} anos"},
        {'label': 'Fins de Semana', 'value': f"{pct_fds:.1f}%"},
    ])

    # =====================================================================
    # SEÇÃO 2: GRÁFICOS DA ANÁLISE GERAL
    # =====================================================================
    _add_section_title(pdf, "Serie Historica de Ocorrencias")

    # Gráfico: Série temporal
    try:
        df_temporal = df_geral.copy()
        if not df_temporal.empty:
            df_temporal['ano_mes'] = df_temporal['data_fato'].dt.to_period('M').astype(str)
            if agrupamento == "Consolidado":
                registros_por_mes_ano = df_temporal.groupby('ano_mes').size().reset_index(name='quantidade').sort_values('ano_mes')
                color_param = None
            else:
                mapa_agrup = {"Município": "municipio", "Mesorregião": "mesoregiao", "Associação": "associacao"}
                col_agrup = mapa_agrup.get(agrupamento, 'municipio')
                registros_por_mes_ano = df_temporal.groupby(['ano_mes', col_agrup], observed=True).size().reset_index(name='quantidade').sort_values('ano_mes')
                color_param = col_agrup

            fig_temporal = plot_serie_temporal(registros_por_mes_ano, "Linha", agrupamento, color_param)
            img = _fig_to_image(fig_temporal, width=1100, height=400)
            _add_image_to_pdf(pdf, img, w=270)
    except Exception:
        pass

    # Gráfico: Por Ano
    pdf.add_page()
    _add_section_title(pdf, "Ocorrencias por Ano e por Mes")

    try:
        if not df_geral.empty:
            ano_corrente = pd.Timestamp.now().year
            if agrupamento == "Consolidado":
                registros_por_ano = df_geral['ano'].value_counts().sort_index().reset_index()
                registros_por_ano.columns = ['ano', 'Quantidade']
                color_param = None
            else:
                mapa_agrup = {"Município": "municipio", "Mesorregião": "mesoregiao", "Associação": "associacao"}
                col_agrup = mapa_agrup.get(agrupamento, 'municipio')
                registros_por_ano = df_geral.groupby(['ano', col_agrup], observed=True).size().reset_index(name='Quantidade')
                color_param = col_agrup

            if not registros_por_ano.empty:
                registros_por_ano['ano'] = registros_por_ano['ano'].apply(
                    lambda x: f'{x} (Parcial)' if x == ano_corrente else str(x)
                )
            fig_ano = plot_por_ano(registros_por_ano, "Barras", agrupamento, color_param)
            img = _fig_to_image(fig_ano, width=550, height=380)
            _add_image_to_pdf(pdf, img, w=130)
    except Exception:
        pass

    # Gráfico: Por Mês
    try:
        if not df_geral.empty:
            meses_ordem = ['January', 'February', 'March', 'April', 'May', 'June',
                           'July', 'August', 'September', 'October', 'November', 'December']
            nomes_meses_pt = {
                'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março',
                'April': 'Abril', 'May': 'Maio', 'June': 'Junho', 'July': 'Julho',
                'August': 'Agosto', 'September': 'Setembro', 'October': 'Outubro',
                'November': 'Novembro', 'December': 'Dezembro'
            }
            df_geral_temp = df_geral.copy()
            df_geral_temp['mes_cat'] = pd.Categorical(df_geral_temp['mes'], categories=meses_ordem, ordered=True)
            registros_por_mes = df_geral_temp['mes_cat'].value_counts().sort_index().reset_index()
            registros_por_mes.columns = ['Mês', 'Quantidade']
            registros_por_mes['Mês'] = registros_por_mes['Mês'].map(nomes_meses_pt)

            fig_mes = plot_por_mes(registros_por_mes, "Barras")
            img = _fig_to_image(fig_mes, width=550, height=380)
            _add_image_to_pdf(pdf, img, w=130)
    except Exception:
        pass

    # Gráfico: Dia da Semana
    pdf.add_page()
    _add_section_title(pdf, "Distribuicao por Dia da Semana e Faixa Etaria")

    try:
        if not df_geral.empty:
            df_geral_temp = df_geral.copy()
            df_geral_temp['dia_semana'] = df_geral_temp['data_fato'].dt.day_name()
            dias_ordem = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            nomes_dias_pt = {
                'Monday': 'Segunda-feira', 'Tuesday': 'Terça-feira', 'Wednesday': 'Quarta-feira',
                'Thursday': 'Quinta-feira', 'Friday': 'Sexta-feira',
                'Saturday': 'Sábado', 'Sunday': 'Domingo'
            }
            df_geral_temp['dia_semana_cat'] = pd.Categorical(df_geral_temp['dia_semana'], categories=dias_ordem, ordered=True)
            registros_por_dia = df_geral_temp['dia_semana_cat'].value_counts().sort_index().reset_index()
            registros_por_dia.columns = ['Dia da Semana', 'Quantidade']
            registros_por_dia['Dia da Semana'] = registros_por_dia['Dia da Semana'].map(nomes_dias_pt)

            fig_dia = plot_dia_semana(registros_por_dia, "Barras")
            img = _fig_to_image(fig_dia, width=550, height=380)
            _add_image_to_pdf(pdf, img, w=130)
    except Exception:
        pass

    # Gráfico: Faixa Etária
    try:
        if not df_geral.empty:
            df_faixa = df_geral.dropna(subset=['idade_vitima']).copy()
            bins = [0, 12, 17, 29, 40, 50, 60, 70, 79, 120]
            labels = ['0-12', '13-17', '18-29', '30-40', '41-50', '51-60', '61-70', '71-79', '80+']
            df_faixa['faixa_etaria'] = pd.cut(df_faixa['idade_vitima'], bins=bins, labels=labels, right=True)
            registros_por_faixa = df_faixa['faixa_etaria'].value_counts().sort_index().reset_index()
            registros_por_faixa.columns = ['Faixa Etária', 'Quantidade']

            fig_faixa = plot_faixa_etaria(registros_por_faixa, "Barras")
            img = _fig_to_image(fig_faixa, width=550, height=380)
            _add_image_to_pdf(pdf, img, w=130)
    except Exception:
        pass

    # Gráfico: Tipo de crime
    pdf.add_page()
    _add_section_title(pdf, "Natureza das Ocorrencias")

    try:
        if not df_geral.empty:
            if agrupamento == "Consolidado":
                registros_por_fato = df_geral['fato_comunicado'].value_counts().reset_index()
                registros_por_fato.columns = ['fato_comunicado', 'Quantidade']
                color_param = None
            else:
                mapa_agrup = {"Município": "municipio", "Mesorregião": "mesoregiao", "Associação": "associacao"}
                col_agrup = mapa_agrup.get(agrupamento, 'municipio')
                registros_por_fato = df_geral.groupby(['fato_comunicado', col_agrup], observed=True).size().reset_index(name='Quantidade')
                color_param = col_agrup

            fig_fato = plot_tipo_crime(registros_por_fato, "Barras", agrupamento, color_param)
            img = _fig_to_image(fig_fato, width=900, height=450)
            _add_image_to_pdf(pdf, img, w=260)
    except Exception:
        pass

    # Gráfico: Vulnerabilidade por faixa etária
    try:
        if not df_geral.empty:
            df_vuln = df_geral.dropna(subset=['idade_vitima']).copy()
            bins = [0, 12, 17, 29, 40, 50, 60, 70, 79, 120]
            labels = ['0-12', '13-17', '18-29', '30-40', '41-50', '51-60', '61-70', '71-79', '80+']
            df_vuln['faixa_etaria'] = pd.cut(df_vuln['idade_vitima'], bins=bins, labels=labels, right=True)
            crime_counts = df_vuln.groupby(['faixa_etaria', 'fato_comunicado'], observed=False).size().unstack(fill_value=0)
            crime_pct = crime_counts.div(crime_counts.sum(axis=1), axis=0) * 100
            crime_pct = crime_pct.reset_index()
            df_plot = crime_pct.melt(id_vars='faixa_etaria', var_name='fato_comunicado', value_name='percentual')

            fig_vuln = plot_barras_vulnerabilidade(df_plot)
            img = _fig_to_image(fig_vuln, width=900, height=450)
            _add_image_to_pdf(pdf, img, w=260)
    except Exception:
        pass

    # =====================================================================
    # SEÇÃO 3: TABELA CONSOLIDADA DE OCORRÊNCIAS
    # =====================================================================
    pdf.add_page()
    _add_section_title(pdf, "Tabela Consolidada de Ocorrencias")

    try:
        if not df_geral.empty:
            if agrupamento != "Consolidado":
                mapa_agrup = {"Município": "municipio", "Mesorregião": "mesoregiao", "Associação": "associacao"}
                col_agrup = mapa_agrup.get(agrupamento, 'municipio')
                tabela = criar_tabela_consolidada(
                    df_geral, col_agrup, agrupamento,
                    df_original_filtrado=df_geral
                )
            else:
                tabela = criar_tabela_total_consolidada(
                    df_geral,
                    df_original_filtrado=df_geral
                )

            if tabela is not None and not tabela.empty:
                # Calcular larguras proporcionais
                n_cols = len(tabela.columns)
                base_w = (pdf.w - 2 * MARGEM) / n_cols
                widths = []
                for col in tabela.columns:
                    col_str = str(col)
                    if 'Fato' in col_str or 'Nome' in col_str or 'Município' in col_str or col_str == agrupamento:
                        widths.append(base_w * 1.8)
                    elif 'Diferença' in col_str:
                        widths.append(base_w * 1.3)
                    elif 'Tendência' in col_str:
                        widths.append(base_w * 1.2)
                    else:
                        widths.append(base_w * 0.8)

                _add_dataframe_table(pdf, tabela, col_widths=widths)
    except Exception:
        pass

    # =====================================================================
    # SEÇÃO 4: TABELA DE TAXA POPULACIONAL
    # =====================================================================
    pdf.add_page()
    _add_section_title(pdf, "Taxa de Ocorrencias por Populacao Feminina")

    try:
        if not df_geral.empty and not df_populacao.empty:
            anos_no_filtro = df_geral['ano'].unique()
            num_anos = len(anos_no_filtro) if len(anos_no_filtro) > 0 else 1
            tabela_pop = criar_tabela_populacional_agrupada(
                df_geral, df_populacao, df_regioes, agrupamento, num_anos
            )
            if tabela_pop is not None and not tabela_pop.empty:
                tabela_pop_reset = tabela_pop.reset_index()
                n_cols = len(tabela_pop_reset.columns)
                usable = pdf.w - 2 * MARGEM
                w_primeira = usable * 0.25
                w_rest = (usable - w_primeira) / (n_cols - 1) if n_cols > 1 else usable
                widths = [w_primeira] + [w_rest] * (n_cols - 1)

                _add_dataframe_table(pdf, tabela_pop_reset, col_widths=widths)
    except Exception:
        pass

    # =====================================================================
    # SEÇÃO 5: RESUMO EXECUTIVO - FEMINICÍDIOS
    # =====================================================================
    pdf.add_page()
    _add_section_title(pdf, "Resumo Executivo -- Analise de Feminicidios")

    total_fem = len(df_feminicidio)
    if total_fem > 0:
        vitimas_bo = df_feminicidio[
            df_feminicidio['bo_de_vd_contra_o_autor'].astype(str).str.upper() == 'SIM'
        ].shape[0]
        pct_bo = (vitimas_bo / total_fem) * 100

        autores_hist = 0
        if 'passagem_por_violencia_domestica' in df_feminicidio.columns:
            autores_hist = df_feminicidio[
                df_feminicidio['passagem_por_violencia_domestica'].astype(str).str.upper() == 'SIM'
            ].shape[0]
        pct_hist = (autores_hist / total_fem) * 100

        _add_kpi_cards(pdf, [
            {'label': 'Total de Feminicidios', 'value': str(total_fem)},
            {'label': '% Vitimas c/ BO Anterior', 'value': f"{pct_bo:.1f}%"},
            {'label': '% Autores c/ Historico VD', 'value': f"{pct_hist:.1f}%"},
        ])
    else:
        pdf.set_font('Helvetica', 'I', 10)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 10, 'Nenhum dado de feminicidio encontrado para os filtros selecionados.', ln=True)

    # =====================================================================
    # SEÇÃO 6: GRÁFICOS DE FEMINICÍDIOS
    # =====================================================================
    if total_fem > 0:
        _add_section_title(pdf, "Serie Temporal de Feminicidios")

        # Gráfico: Série temporal feminicídios
        try:
            df_fem_temp = df_feminicidio.copy()
            df_fem_temp['ano_mes'] = df_fem_temp['data_fato'].dt.to_period('M').astype(str)
            if agrupamento == "Consolidado":
                fem_por_mes = df_fem_temp.groupby('ano_mes').size().reset_index(name='Quantidade')
                color_param = None
            else:
                mapa_agrup = {"Município": "municipio", "Mesorregião": "mesoregiao", "Associação": "associacao"}
                col_agrup = mapa_agrup.get(agrupamento, 'municipio')
                fem_por_mes = df_fem_temp.groupby(['ano_mes', col_agrup], observed=True).size().reset_index(name='Quantidade')
                color_param = col_agrup
            fem_por_mes.rename(columns={'ano_mes': 'Mês/Ano'}, inplace=True)

            fig_fem_serie = plot_feminicidio_serie_temporal(fem_por_mes, "Barras", agrupamento, color_param)
            img = _fig_to_image(fig_fem_serie, width=1100, height=400)
            _add_image_to_pdf(pdf, img, w=270)
        except Exception:
            pass

        # Gráfico: Feminicídios por ano
        pdf.add_page()
        _add_section_title(pdf, "Feminicidios por Ano e Perfil")

        try:
            ano_corrente = pd.Timestamp.now().year
            if agrupamento == "Consolidado":
                fem_por_ano = df_feminicidio['ano'].value_counts().sort_index().reset_index()
                fem_por_ano.columns = ['ano', 'Quantidade']
                color_param = None
            else:
                mapa_agrup = {"Município": "municipio", "Mesorregião": "mesoregiao", "Associação": "associacao"}
                col_agrup = mapa_agrup.get(agrupamento, 'municipio')
                fem_por_ano = df_feminicidio.groupby(['ano', col_agrup], observed=True).size().reset_index(name='Quantidade')
                color_param = col_agrup

            if not fem_por_ano.empty:
                fem_por_ano['ano'] = fem_por_ano['ano'].apply(
                    lambda x: f'{x} (Parcial)' if x == ano_corrente else str(x)
                )
            fig_fem_ano = plot_feminicidio_por_ano(fem_por_ano, "Barras", agrupamento, color_param)
            img = _fig_to_image(fig_fem_ano, width=550, height=380)
            _add_image_to_pdf(pdf, img, w=130)
        except Exception:
            pass

        # Gráfico: Vínculo com o autor
        try:
            if agrupamento == "Consolidado":
                vinculo = df_feminicidio['relacao_autor'].value_counts().reset_index()
                vinculo.columns = ['relacao_autor', 'Quantidade']
                color_param = None
            else:
                mapa_agrup = {"Município": "municipio", "Mesorregião": "mesoregiao", "Associação": "associacao"}
                col_agrup = mapa_agrup.get(agrupamento, 'municipio')
                vinculo = df_feminicidio.groupby(['relacao_autor', col_agrup], observed=True).size().reset_index(name='Quantidade')
                color_param = col_agrup

            fig_vinculo = plot_vinculo_autor(vinculo, "Barras", agrupamento, color_param)
            img = _fig_to_image(fig_vinculo, width=550, height=380)
            _add_image_to_pdf(pdf, img, w=130)
        except Exception:
            pass

        # Gráfico: Meio do crime + Autor preso
        pdf.add_page()
        _add_section_title(pdf, "Meio Utilizado e Situacao do Autor")

        try:
            if agrupamento == "Consolidado":
                meio = df_feminicidio['meio_crime'].value_counts().reset_index()
                meio.columns = ['meio_crime', 'Quantidade']
                color_param = None
            else:
                mapa_agrup = {"Município": "municipio", "Mesorregião": "mesoregiao", "Associação": "associacao"}
                col_agrup = mapa_agrup.get(agrupamento, 'municipio')
                meio = df_feminicidio.groupby(['meio_crime', col_agrup], observed=True).size().reset_index(name='Quantidade')
                color_param = col_agrup

            fig_meio = plot_meio_crime(meio, "Barras", agrupamento, color_param)
            img = _fig_to_image(fig_meio, width=550, height=380)
            _add_image_to_pdf(pdf, img, w=130)
        except Exception:
            pass

        try:
            preso = df_feminicidio['autor_preso'].value_counts().reset_index()
            preso.columns = ['Resposta', 'Quantidade']
            fig_preso = plot_autor_preso(preso, "Barras")
            img = _fig_to_image(fig_preso, width=550, height=380)
            _add_image_to_pdf(pdf, img, w=130)
        except Exception:
            pass

        # Gráfico: BO contra o autor
        try:
            bo = df_feminicidio['bo_de_vd_contra_o_autor'].value_counts().reset_index()
            bo.columns = ['Resposta', 'Quantidade']
            _add_subsection_title(pdf, "Vitima possuia BO contra o autor?")
            fig_bo = plot_bo_contra_autor(bo, "Barras")
            img = _fig_to_image(fig_bo, width=550, height=350)
            _add_image_to_pdf(pdf, img, w=130)
        except Exception:
            pass

    # =====================================================================
    # SEÇÃO 7: TABELA CONSOLIDADA DE FEMINICÍDIOS
    # =====================================================================
    pdf.add_page()
    _add_section_title(pdf, "Tabela Consolidada de Feminicidios")

    try:
        if not df_feminicidio.empty:
            if agrupamento != "Consolidado":
                mapa_agrup = {"Município": "municipio", "Mesorregião": "mesoregiao", "Associação": "associacao"}
                col_agrup = mapa_agrup.get(agrupamento, 'municipio')
                tabela_fem = criar_tabela_feminicidio_agrupado(
                    df_feminicidio, col_agrup, agrupamento,
                    df_original_filtrado=df_feminicidio
                )
            else:
                tabela_fem = criar_tabela_total_feminicidio(
                    df_feminicidio,
                    df_original_filtrado=df_feminicidio
                )

            if tabela_fem is not None and not tabela_fem.empty:
                n_cols = len(tabela_fem.columns)
                base_w = (pdf.w - 2 * MARGEM) / n_cols
                widths = []
                for col in tabela_fem.columns:
                    col_str = str(col)
                    if 'Nome' in col_str or 'Município' in col_str or 'Tipo' in col_str or col_str == agrupamento:
                        widths.append(base_w * 1.8)
                    elif 'Diferença' in col_str:
                        widths.append(base_w * 1.3)
                    elif 'Tendência' in col_str:
                        widths.append(base_w * 1.2)
                    else:
                        widths.append(base_w * 0.8)

                _add_dataframe_table(pdf, tabela_fem, col_widths=widths)
    except Exception:
        pass

    # =====================================================================
    # SEÇÃO 8: ÍNDICE DE LETALIDADE
    # =====================================================================
    if agrupamento != "Consolidado" and not df_geral.empty and not df_feminicidio.empty:
        pdf.add_page()
        _add_section_title(pdf, "Indice de Letalidade da Violencia")

        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(*CINZA_TEXTO)
        pdf.multi_cell(0, 5,
            'O indice representa: "Para cada 100 ocorrencias de violencia contra a mulher, '
            'X resultaram em morte." Um indice alto, mesmo com poucas ocorrencias, e sinal de alerta.'
        )
        pdf.ln(5)

        try:
            df_letalidade = calcular_indice_letalidade(df_geral, df_feminicidio, agrupamento)
            if df_letalidade is not None and not df_letalidade.empty:
                df_ranking = df_letalidade.rename(columns={
                    'localidade': agrupamento,
                    'total_eventos': 'Total Eventos',
                    'total_ocorrencias': 'Ocorrências',
                    'total_feminicidios': 'Feminicídios',
                    'indice_letalidade': 'Ind. Letalidade'
                })

                n_cols = len(df_ranking.columns)
                usable = pdf.w - 2 * MARGEM
                w_primeira = usable * 0.30
                w_rest = (usable - w_primeira) / (n_cols - 1) if n_cols > 1 else usable
                widths = [w_primeira] + [w_rest] * (n_cols - 1)

                _add_dataframe_table(pdf, df_ranking, col_widths=widths, max_rows=50)
        except Exception:
            pass

    # =====================================================================
    # EXPORTAR PDF
    # =====================================================================
    pdf_output = pdf.output()
    return bytes(pdf_output)
