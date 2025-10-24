import os

# Caminho da pasta onde estão os arquivos
pasta = r"D:\Search\desafios_python\add-extension-jpg\photos"

# Percorre todos os arquivos da pasta
for nome_arquivo in os.listdir(pasta):
    caminho_completo = os.path.join(pasta, nome_arquivo)
    
    # Ignora subpastas
    if os.path.isfile(caminho_completo):
        # Verifica se o arquivo não tem extensão
        if not os.path.splitext(nome_arquivo)[1]:
            novo_nome = nome_arquivo + ".jpg"
            novo_caminho = os.path.join(pasta, novo_nome)
            
            os.rename(caminho_completo, novo_caminho)
            print(f"Renomeado: {nome_arquivo} → {novo_nome}")

print("✅ Extensões .jpg adicionadas com sucesso!")
