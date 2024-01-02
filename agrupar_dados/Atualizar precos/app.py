import pandas as pd

# Caminho para o arquivo Excel existente
caminho_arquivo_existente = r'C:\Users\tudot\Documents\Relatórios\desafios_python\agrupar_dados\Atualizar precos\precos.xlsx'

caminho_novos_dados = r'C:\Users\tudot\Documents\Relatórios\desafios_python\agrupar_dados\Atualizar precos\dados.xlsx'

# Ler os dados existentes e os novos dados
df_existente = pd.read_excel(caminho_arquivo_existente)
df_novos_dados = pd.read_excel(caminho_novos_dados)

# Exibir os dados existentes
print("Dados existentes:")
print(df_existente)

# Exibir os novos dados
print("\nNovos dados:")
print(df_novos_dados)

# Mesclar os dataframes usando o CODIGO PRODUTO como chave
df_resultado = pd.merge(df_novos_dados, df_existente[['CODIGO PRODUTO', 'Preco atacado']], on='CODIGO PRODUTO', how='left')

# Renomear a coluna de Preco atacado resultante da mesclagem
df_resultado = df_resultado.rename(columns={'Preco atacado': 'Novo Preço'})

# Exibir o resultado
print("\nResultado da mesclagem:")
print(df_resultado)

df_resultado.to_excel(caminho_novos_dados, index=False)
