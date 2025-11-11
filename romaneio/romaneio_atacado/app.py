import os
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# === Caminhos ===
caminho_excel = r"D:\Search\desafios_python\romaneio\romaneio_simples\pedido.xlsx"
caminho_pasta_imagens = r"D:\Search\desafios_python\romaneio\romaneio_simples\photos"
caminho_logo = r"D:\Search\desafios_python\romaneio\romaneio_simples\logo.jpg"

# === Lê o Excel ===
df = pd.read_excel(caminho_excel)

# === Extrai informações do primeiro registro ===
info = df.iloc[0]
codigo_pedido = str(info["PEDIDO"]) if "PEDIDO" in df.columns and pd.notna(info["PEDIDO"]) else "SEM_PEDIDO"

# === Caminho dinâmico de saída ===
caminho_pdf_saida = fr"D:\Search\desafios_python\romaneio\romaneio_{codigo_pedido}.pdf"

# === Estilos ===
styles = getSampleStyleSheet()

titulo_style = ParagraphStyle(
    "titulo",
    parent=styles["Title"],
    fontSize=14,
    alignment=TA_LEFT,
    spaceAfter=4
)

subtitulo_style = ParagraphStyle(
    "subtitulo",
    parent=styles["Normal"],
    fontSize=8,
    alignment=TA_LEFT,
    textColor=colors.HexColor("#333333"),
    spaceAfter=6,
)

# Estilo reduzido e centralizado para totais
estilo_total = ParagraphStyle(
    "total_menor",
    parent=styles["Normal"],
    fontSize=5.5,
    alignment=TA_CENTER,
    spaceAfter=0,
    spaceBefore=0,
)

# Estilo para texto com quebra controlada
wrap_style = ParagraphStyle(
    "wrap",
    parent=styles["Normal"],
    fontSize=6,
    leading=7,
    alignment=TA_CENTER,
    wordWrap="LTR",
)

header_style = ParagraphStyle(
    "header",
    parent=styles["Normal"],
    fontSize=6.5,
    leading=7,
    alignment=TA_CENTER,
    textColor=colors.black,
    wordWrap="LTR",
)

espacador = Spacer(1, 2)
elementos = []

# === Cabeçalho com logo e título lado a lado ===
nome_cliente = str(info["CLIENTE"]) if "CLIENTE" in df.columns and pd.notna(info["CLIENTE"]) else ""
codigo_cliente = str(info["COD"]) if "COD" in df.columns and pd.notna(info["COD"]) else ""
codigo_condpgto = str(info["CONDPGTO"]) if "CONDPGTO" in df.columns and pd.notna(info["CONDPGTO"]) else ""
codigo_parcelas = str(info["QTD-PARCELAS"]) if "QTD-PARCELAS" in df.columns and pd.notna(info["QTD-PARCELAS"]) else ""
codigo_transport = str(info["TRANSPORT"]) if "TRANSPORT" in df.columns and pd.notna(info["TRANSPORT"]) else ""
codigo_cnpj = str(info["CNPJ"]) if "CNPJ" in df.columns and pd.notna(info["CNPJ"]) else ""
codigo_cidade = str(info["CIDADE"]) if "CIDADE" in df.columns and pd.notna(info["CIDADE"]) else ""
codigo_uf = str(info["UF"]) if "UF" in df.columns and pd.notna(info["UF"]) else ""

titulo = Paragraph("<b>PEDIDO DE VENDA</b>", titulo_style)
subtitulo = Paragraph(f"<b>PEDIDO:</b> {codigo_pedido} &nbsp;&nbsp;&nbsp; <b>CLIENTE:</b> {codigo_cliente} - {nome_cliente}", subtitulo_style)
pgto = Paragraph(f"<b>FORMA DE PGTO:</b> {codigo_parcelas}", subtitulo_style)
transport = Paragraph(f"<b>TRANSPORT:</b> {codigo_transport}", subtitulo_style)
end = Paragraph(f"<b>CNPJ:</b> {codigo_cnpj} &nbsp;&nbsp;&nbsp; <b>CIDADE:</b> {codigo_cidade} &nbsp;&nbsp;&nbsp; <b>UF:</b> {codigo_uf}", subtitulo_style)
bloco_texto = [titulo, subtitulo, pgto, transport, end]

if os.path.exists(caminho_logo):
    logo = Image(caminho_logo, width=60, height=60)
else:
    logo = Paragraph(" ", styles["Normal"])

tabela_topo = Table([[bloco_texto, logo]], colWidths=[440, 60])
tabela_topo.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("ALIGN", (0, 0), (0, 0), "LEFT"),   
    ("LEFTPADDING", (0, 0), (0, 0), -20),  
    ("RIGHTPADDING", (0, 0), (0, 0), 4),
    ("ALIGN", (1, 0), (1, 0), "RIGHT"),  
]))

elementos.append(tabela_topo)
elementos.append(espacador)

# === Colunas a exibir ===
colunas_exibir = [
    "IMAGEM", "PRODUTO", "TAMANHO", "COR", "COLECAO",
    "REFERENCIA", "FAMILIA", "QTD-SOLICITADA", "VLR-SOLICITADO"
]

nomes_cabecalho = {
    "IMAGEM": "FOTO",
    "PRODUTO": "DESCRIÇÃO DO PRODUTO",
    "TAMANHO": "TAM.",
    "COR": "COR",
    "COLECAO": "COLEÇÃO",
    "REFERENCIA": "REF.",
    "FAMILIA": "FAMÍLIA",
    "QTD-SOLICITADA": "QTD",
    "VLR-SOLICITADO": "VALOR (R$)"
}

# Cria cabeçalho formatado com Paragraphs
cabecalho = [[Paragraph(nomes_cabecalho.get(c, c), header_style) for c in colunas_exibir]]
dados_tabela = []

# === Gera as linhas da tabela ===
for _, linha in df.iterrows():
    linha_dados = []
    for col in colunas_exibir:
        if col == "IMAGEM":
            nome_img = str(linha[col]).strip() if pd.notna(linha[col]) else ""
            caminho_img = os.path.join(caminho_pasta_imagens, f"{nome_img}.jpg")
            if os.path.exists(caminho_img):
                linha_dados.append(Image(caminho_img, width=35, height=35))
            else:
                linha_dados.append(Paragraph("-", wrap_style))

        elif col == "VLR-SOLICITADO":
            try:
                valor = float(linha[col])
                valor_formatado = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except:
                valor_formatado = "R$ 0,00"
            linha_dados.append(Paragraph(valor_formatado, wrap_style))

        elif col == "QTD-SOLICITADA":
            qtd = str(linha[col]) if pd.notna(linha[col]) else ""
            linha_dados.append(Paragraph(qtd, wrap_style))

        else:
            valor = str(linha[col]) if pd.notna(linha[col]) else ""
            linha_dados.append(Paragraph(valor, wrap_style))

    dados_tabela.append(linha_dados)

# === Soma total ===
total_qtd = df["QTD-SOLICITADA"].sum() if "QTD-SOLICITADA" in df.columns else 0
total_valor = df["VLR-SOLICITADO"].sum() if "VLR-SOLICITADO" in df.columns else 0

total_qtd_formatado = f"{int(total_qtd)}"
total_valor_formatado = f"R$ {total_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

linha_total = [
    "",  # IMAGEM
    Paragraph("<b>TOTAL GERAL</b>", estilo_total),
    "", "", "", "", "",  # colunas intermediárias
    Paragraph(f"<b>{total_qtd_formatado}</b>", estilo_total),
    Paragraph(f"<b>{total_valor_formatado}</b>", estilo_total),
]
dados_tabela.append(linha_total)

# === Monta tabela com alinhamento de cabeçalho ===
larguras_colunas = [45, 160, 30, 60, 50, 45, 45, 40, 70]
altura_cabecalho = 16

tabela = Table(cabecalho + dados_tabela, repeatRows=1, colWidths=larguras_colunas)
tabela.setStyle(TableStyle([
    # Cabeçalho
    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
    ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
    ("FONTSIZE", (0, 0), (-1, 0), 6.5),
    ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
    ("TOPPADDING", (0, 0), (-1, 0), 4),

    # Corpo
    ("ALIGN", (0, 1), (-1, -1), "CENTER"),
    ("VALIGN", (0, 1), (-1, -1), "MIDDLE"),
    ("FONTSIZE", (0, 1), (-1, -1), 6),
    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),

    # Linha total
    ("BACKGROUND", (0, -1), (-1, -1), colors.whitesmoke),
    ("SPAN", (0, -1), (1, -1)),
    ("ALIGN", (0, -1), (-1, -1), "CENTER"),
    ("VALIGN", (0, -1), (-1, -1), "MIDDLE"),
]))

# Força altura visual uniforme no cabeçalho
tabela._argH[0] = altura_cabecalho

elementos.append(tabela)

# === Cria PDF ===
pdf = SimpleDocTemplate(
    caminho_pdf_saida,
    pagesize=A4,
    leftMargin=5,   
    rightMargin=15,
    topMargin=20,
    bottomMargin=20,
)
pdf.build(elementos)

print("✅ PDF com cabeçalho alinhado e layout profissional gerado com sucesso!")
print(f"📂 Arquivo salvo em: {caminho_pdf_saida}")
