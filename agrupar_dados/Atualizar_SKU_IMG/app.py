import pandas as pd

# Caminho para os arquivos
caminho_arquivo_existente = r'agrupar_dados/Atualizar_SKU_IMG/Lista.xlsx'
caminho_novos_dados = r'D:\Search\desafios_python\agrupar_dados\Atualizar_SKU_IMG\novos.xlsx'
caminho_sku_imagem = r'D:\Search\desafios_python\agrupar_dados\Atualizar_SKU_IMG\data.xlsx'

# Ler os dados
df_existente = pd.read_excel(caminho_arquivo_existente)
df_novos_dados = pd.read_excel(caminho_novos_dados)
df_sku_imagem = pd.read_excel(caminho_sku_imagem)

# Exibir os dados
print("Dados existentes:")
print(df_existente)

print("\nNovos dados:")
print(df_novos_dados)

print("\nSKU e Imagem:")
print(df_sku_imagem)

# Mesclar os dataframes usando o SKU como chave
df_resultado = pd.merge(df_novos_dados, df_sku_imagem[['SKU', 'Imagem']], on='SKU', how='left')

# Exibir o resultado
print("\nResultado da mesclagem com imagem:")
print(df_resultado)

# Salvar o resultado em um novo arquivo Excel
df_resultado.to_excel(caminho_novos_dados, index=False)
