import pandas as pd

# Caminhos dos arquivos
caminho_tabela_1 = r'C:\Users\Lagea\OneDrive\Documentos\desafios_python-main\desafios_python-main\agrupar_dados\Atualizar Notas FIcais\sieg.xlsx'  # Tabela com colunas: Nota, CnpjEmit, etc.
caminho_tabela_2 = r'C:\Users\Lagea\OneDrive\Documentos\desafios_python-main\desafios_python-main\agrupar_dados\Atualizar Notas FIcais\totvs.xlsx' # Tabela com colunas: Nota (ou 'Nota ' com espaço), etc.

# Leitura dos arquivos
df1 = pd.read_excel(caminho_tabela_1)
df2 = pd.read_excel(caminho_tabela_2)

# Corrigindo possíveis espaços no nome da coluna
df2.columns = df2.columns.str.strip()

# Comparar pela coluna 'Nota' (certifique-se de que ambas têm essa coluna)
if 'Nota' not in df1.columns:
    raise ValueError("Coluna 'Nota' não encontrada na tabela 1")
if 'Nota' not in df2.columns:
    raise ValueError("Coluna 'Nota' não encontrada na tabela 2")

# Filtra as notas que estão em df1 e **não** estão em df2
notas_nao_encontradas = df1[~df1['Nota'].isin(df2['Nota'])]

# Salva o resultado
caminho_resultado = r'C:\Users\Lagea\OneDrive\Documentos\desafios_python-main\desafios_python-main\agrupar_dados\Atualizar Notas FIcais\resultado_notas_faltantes.xlsx'
notas_nao_encontradas.to_excel(caminho_resultado, index=False)

# Exibe o resultado
print(notas_nao_encontradas)
