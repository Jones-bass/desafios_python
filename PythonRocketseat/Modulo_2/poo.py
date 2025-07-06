# POO

# Classe exemplo
class Pessoa:
  def __init__(self, nome, idade, altura) -> None:
    self.nome = nome
    self.idade = idade
    self.altura = altura


  def saudacao(self):
    return f"Olá, meu nome é {self.nome} e eu tenho {self.idade} anos com altura de {self.altura}."

# Objetos
pessoa1 = Pessoa("Alice", 30, 1.75)
mensagem = pessoa1.saudacao()
print(mensagem)

pessoa2 = Pessoa(nome="Rodrigo", idade=32, altura=1.91)
mensagem = pessoa2.saudacao()
print(mensagem)