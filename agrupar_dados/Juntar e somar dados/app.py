import pandas as pd

# Caminho para o arquivo Excel existente
caminho_arquivo_existente = r'C:\Users\tudot\OneDrive\Área de Trabalho\Python - Juntar e somar dados\dados.xlsx'

caminho_novo = r'C:\Users\tudot\OneDrive\Área de Trabalho\Python - Juntar e somar dados\novos.xlsx'

import pandas as pd

# Ler o arquivo Excel
df = pd.read_excel(caminho_arquivo_existente)

# Agrupar os dados por Nome e somar os valores
soma_por_empresa = df.groupby('Nome').sum()

# Exibir resultados
print(soma_por_empresa)

soma_por_empresa.to_excel(caminho_novo)
