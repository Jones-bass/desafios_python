import pandas as pd

# Caminhos dos arquivos
caminho_tabela_principal = r'C:\Users\Lagea\OneDrive\Documentos\desafios_python-main\desafios_python-main\agrupar_dados\Atualizar SKU\data.xlsx'
caminho_tabela_estoque = r'C:\Users\Lagea\OneDrive\Documentos\desafios_python-main\desafios_python-main\agrupar_dados\Atualizar SKU\novos.xlsx'

# Leitura dos arquivos
df_principal = pd.read_excel(caminho_tabela_principal)
df_estoque = pd.read_excel(caminho_tabela_estoque)

# Verifica se a coluna 'ESTOQUE' existe
if 'ESTOQUE' not in df_estoque.columns:
    raise ValueError("A coluna 'ESTOQUE' não está presente no arquivo de estoque.")

# Faz a junção com base na coluna 'SKU'
df_resultado = df_principal.merge(df_estoque[['SKU', 'ESTOQUE']], on='SKU', how='left')

# Preenche os NaNs com 0 e transforma para inteiro
df_resultado['ESTOQUE'] = df_resultado['ESTOQUE'].fillna(0).astype(int)

# Salva a atualização
df_resultado.to_excel(caminho_tabela_principal, index=False)

# Exibe o resultado
print(df_resultado)
