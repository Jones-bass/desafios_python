import pandas as pd

# Caminho para o arquivo Excel existente
caminho_arquivo_existente = r'C:\Users\tudot\OneDrive\Área de Trabalho\Python - Atualizar Quantidade\dados.xlsx'

# Caminho para o arquivo Excel com os novos dados
caminho_novos_dados = r'C:\Users\tudot\OneDrive\Área de Trabalho\Python - Atualizar Quantidade\novos.xlsx'

# Ler os dados existentes e os novos dados
df_existente = pd.read_excel(caminho_arquivo_existente)
df_novos_dados = pd.read_excel(caminho_novos_dados)

# Exibir os dados existentes
print("Dados existentes:")
print(df_existente)

# Exibir os novos dados
print("\nNovos dados:")
print(df_novos_dados)

# Atualizar as quantidades com base nos códigos dos produtos
df_existente['Quantidade'] = df_existente['Código'].map(df_novos_dados.set_index('Código')['Quantidade'])

# Preencher valores nulos (NaN) com 0
df_existente['Quantidade'].fillna(0, inplace=True)

# Exibir os dados atualizados
print("\nDados atualizados:")
print(df_existente)

# Salvar os dados atualizados de volta no arquivo Excel existente
df_existente.to_excel(caminho_arquivo_existente, index=False)
