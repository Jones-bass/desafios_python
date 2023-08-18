'''O sistema de login deve permitir que novos usuários sejam cadastrados, e que usuários existentes possam fazer o login. O sistema deve alertar caso a senha e login não estejam corretos.'''

resposta = input('[1] - Cadastrar novo usuário [2] - Fazer login: ')
# armazenando os usuários existentes
usuarios = ['carol','amanda','jeff']
senhas = ['123456','abcdef','123abcd']

if resposta == '1':
    # recebendo um usuário
    usuario_digitado = input('digite seu usuário: ')
    # O sistema não deve permitir que usuário duplicados sejam cadastrados
    if usuario_digitado in usuarios:
        print('usuário existente')
    else:
        # recebendo uma senha
        senha_digitada = input('Digite sua senha: ')
        # caso não existe, cadastrar aquele usuário e senha
        usuarios.append(usuario_digitado)
        senhas.append(senha_digitada)
elif resposta == '2':
    # Permitir que usuários existentes possam fazer o login
    # pedir usuário
    usuario_digitado = input('Digite seu usuário: ')
    # pedir senha
    senha_digitada = input('Digite sua senha: ')
    # preciso verificar se a senha providênciada para aquele usuário é a mesma senha que está na nossa lista de senhas
    encontrado = False
    for indice, usuario in enumerate(usuarios):
        if usuario_digitado == usuario and senha_digitada == senhas[indice]:
            print('Login feito com sucesso')
            encontrado = True
        elif encontrado == False:
            # O sistema deve alertar caso a senha e login não estejam corretos.
            print('usuário ou senha incorreto!')
else:
    print('digite apenas 1 ou 2')
