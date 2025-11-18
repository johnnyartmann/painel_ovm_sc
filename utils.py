import io
import re
import unicodedata

import numpy as np
import pandas as pd


def normalizar_nome(texto):
    """
    Limpa e padroniza uma string de texto para ser usada como
    chave de junção.
    """
    if not isinstance(texto, str):
        return ""

    texto = texto.lower()

    # --- 1. Mapa de Exceções (Hard-coded) ---
    mapa_excecoes = {
        'herval': 'herval d oeste'
        # (Mantemos a correção para o arquivo Geo)
    }
    if texto in mapa_excecoes:
        texto = mapa_excecoes[texto]

    # --- 2. Normalização de Acentos ---
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto)
                    if unicodedata.category(c) != 'Mn')

    # --- 3. Normalização de Pontuação ---
    # Substitui qualquer coisa que NÃO seja (^) letra (a-z),
    # número (0-9) ou espaço (\s) por um espaço.
    texto = re.sub(r'[^a-z0-9\s]', ' ', texto)

    # --- 4. Normalização de Palavras ---
    # Remove artigos/preposições (agora cercados por espaços)
    texto = re.sub(r'\b(de|do|da|d)\b', ' ', texto)

    # --- 5. Limpeza Final ---
    # Remove espaços múltiplos (criados pelas substituições)
    texto = re.sub(r'\s+', ' ', texto).strip()

    return texto.upper()


def to_excel(df):
    """Converte um DataFrame para um arquivo Excel em memória."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados')
    processed_data = output.getvalue()
    return processed_data


def to_csv(df):
    """Converte um DataFrame para um arquivo CSV em memória."""
    return df.to_csv(index=False).encode('utf-8')


def colorir_percentual(val):
    """Retorna a cor para o valor percentual."""
    if pd.isna(val) or val == 0:
        return ''
    color = 'red' if val > 0 else 'green'
    return f'color: {color}'


def formatar_seta_percentual(val):
    """Formata o valor com seta e percentual."""
    if pd.isna(val):
        return '-'
    seta = '▲' if val > 0 else '▼' if val < 0 else ''
    if seta:
        return f'{seta} {abs(val):.2f}%'
    return f'{abs(val):.2f}%'


def calcular_cagr(valor_inicial, valor_final, num_anos):
    """Calcula a Taxa de Crescimento Anual Composta (CAGR)."""
    if isinstance(valor_inicial, pd.Series):
        cagr = pd.Series(np.nan, index=valor_inicial.index, dtype='float64')
        if num_anos < 3:
            return cagr

        mask = (valor_inicial.notna()) & (valor_final.notna()) & (valor_inicial != 0)

        cagr.loc[mask] = ((valor_final[mask] / valor_inicial[mask]) ** (1 / (num_anos - 1)) - 1) * 100
        return cagr
    else:
        if pd.isna(valor_inicial) or pd.isna(valor_final) or valor_inicial == 0 or num_anos < 3:
            return np.nan
        return ((valor_final / valor_inicial) ** (1 / (num_anos - 1)) - 1) * 100
