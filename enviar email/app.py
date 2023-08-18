import smtplib
import email.message

import pandas as pd


tabela_vendas = pd.read_excel(r'C:\Users\tudot\Videos\Intervenção Phayton\Jornada Python 01.22\Aula 1\desafios_python\enviar email\Vendas.xlsx')

## Tabela de Faturamento
tabela_faturamento = tabela_vendas[['ID Loja', 'Valor Final']].groupby('ID Loja').sum() ## filtrando a tabela com os campos especificos, agrupadar linhas repetidas e somar 
tabela_faturamento = tabela_faturamento.sort_values(by='Valor Final', ascending=False) ## Ordenando tabela crescente ou descente 

## Tabela de quantidade
tabela_quantidade = tabela_vendas[['ID Loja', 'Quantidade']].groupby('ID Loja').sum() ## filtrando a tabela com os campos especificos, agrupadar linhas repetidas e somar 
tabela_quantidade = tabela_quantidade.sort_values(by='Quantidade', ascending=False) ## Ordenando tabela crescente ou descente 

## Divisão do valor final com a quantidade
ticket_medio = tabela_faturamento['Valor Final'] / tabela_quantidade['Quantidade']
ticket_medio = ticket_medio.sort_values(ascending=False) ## Ordenando tabela crescente ou descente 


def enviar_email(nome_da_loja, tabela):
    import smtplib
    import email.message

    server = smtplib.SMTP('smtp.gmail.com:587') 
    corpo_email = f"""
    <p>Prezados,<p>
    <p>Segue Relatório de Vendas - {nome_da_loja}<p>
    {tabela.to_html()}
    """

    msg = email.message.Message()
    msg['Subject'] = f"Relatório de Vendas - {nome_da_loja}"
    msg['From'] = 'jonesbass.tb@gmail.com'
    msg['To'] = 'jonesbass.tb@gmail.com'
    password = ""  
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(corpo_email)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    # Login Credentials for sending the mail
        smtp.login(msg['From'], password)
        smtp.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
        print('Email enviado')

enviar_email("Diretoria", tabela_faturamento)