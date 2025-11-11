import os
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

# === Caminhos ===
caminho_excel = r"D:\Search\desafios_python\romaneio\romaneio_catalogo\produtos.xlsx"
caminho_pasta_imagens = r"D:\Search\desafios_python\romaneio\romaneio_catalogo\photos"
caminho_logo = r"D:\Search\desafios_python\romaneio\romaneio_catalogo\logo.jpg"
caminho_pdf_saida = r"D:\Search\desafios_python\romaneio\romaneio_catalogo\lista_produtos.pdf"

# === Lê o Excel ===
df = pd.read_excel(caminho_excel)

# === Estilos ===
styles = getSampleStyleSheet()

titulo_style = ParagraphStyle(
    "titulo",
    parent=styles["Title"],
    fontSize=16,
    alignment=TA_LEFT,
    textColor=colors.HexColor("#555555"),  # 🎨 Cinza suave para um visual elegante
    spaceAfter=4
)

header_style = ParagraphStyle(
    "header",
    parent=styles["Normal"],
    fontSize=7,
    leading=8,
    alignment=TA_CENTER,
    textColor=colors.black,
)

wrap_style = ParagraphStyle(
    "wrap",
    parent=styles["Normal"],
    fontSize=6.5,
    leading=7,
    alignment=TA_CENTER,
    wordWrap="LTR",
)

# === Cabeçalho com título à esquerda e logo à direita ===
titulo = Paragraph("<b>Catálogo Interno</b>", titulo_style)

if os.path.exists(caminho_logo):
    logo = Image(caminho_logo, width=80 , height=80  )
else:
    logo = Paragraph(" ", styles["Normal"])

# Título à esquerda, logo à direita
tabela_topo = Table([[titulo, logo]], colWidths=[470, 70])
tabela_topo.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ALIGN", (0, 0), (0, 0), "LEFT"),
    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
]))

elementos = [tabela_topo, Spacer(1, 10)]

# === Colunas ===
colunas_exibir = [
    "SKU", "Imagem", "ITEM", "DESCRICAO", "TAMANHO", "COLECAO", "REFERENCIA", "FAMILIA",
    "COR", "VAREJO", "Barra" 
]

nomes_cabecalho = {
    "SKU": "SKU",
    "Imagem": "IMAGEM",
    "ITEM": "ITEM",
    "DESCRICAO": "DESCRIÇÃO",
    "TAMANHO": "TAM",
    "COLECAO": "COLEÇÃO",
    "REFERENCIA": "REF",
    "FAMILIA": "FAMÍLIA",
    "COR": "COR",
    "VAREJO": "VALOR",
    "Barra": "BARRA"
}

# === Cabeçalho da tabela ===
cabecalho = [[Paragraph(nomes_cabecalho.get(c, c), header_style) for c in colunas_exibir]]

# === Dados ===
dados_tabela = []
for _, linha in df.iterrows():
    linha_dados = []
    for col in colunas_exibir:
        if col == "Imagem":
            nome_img = str(linha[col]).strip() if pd.notna(linha[col]) else ""
            caminho_img = os.path.join(caminho_pasta_imagens, f"{nome_img}.jpg")
            if os.path.exists(caminho_img):
                linha_dados.append(Image(caminho_img, width=45, height=45))
            else:
                linha_dados.append(Paragraph("-", wrap_style))

        elif col == "VAREJO":
            try:
                valor_str = str(linha[col]).replace("R$", "").strip()
                valor_str = valor_str.replace(".", "").replace(",", ".") if "," in valor_str else valor_str
                valor = float(valor_str)
                valor_formatado = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except:
                valor_formatado = "R$ 0,00"
            linha_dados.append(Paragraph(valor_formatado, wrap_style))

        else:
            valor = str(linha[col]) if pd.notna(linha[col]) else ""
            linha_dados.append(Paragraph(valor, wrap_style))
    dados_tabela.append(linha_dados)

# === Monta tabela ===
larguras_colunas = [ 30, 50, 45, 118, 40, 50, 40, 40, 50, 50, 59 ]

tabela = Table(cabecalho + dados_tabela, repeatRows=1, colWidths=larguras_colunas)
tabela.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
    ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
    ("FONTSIZE", (0, 0), (-1, 0), 7),
    ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
    ("TOPPADDING", (0, 0), (-1, 0), 4),
    ("ALIGN", (0, 1), (-1, -1), "CENTER"),
    ("VALIGN", (0, 1), (-1, -1), "MIDDLE"),
    ("FONTSIZE", (0, 1), (-1, -1), 6),
    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
]))

elementos.append(tabela)

# === Cria PDF ===
pdf = SimpleDocTemplate(
    caminho_pdf_saida,
    pagesize=A4,
    leftMargin=10,
    rightMargin=10,
    topMargin=20,
    bottomMargin=20,
)

pdf.build(elementos)

print("✅ Catálogo Interno gerado com sucesso!")
print(f"📂 Arquivo salvo em: {caminho_pdf_saida}")
