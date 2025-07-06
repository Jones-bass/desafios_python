from flask import Flask, request, jsonify
from models.task import Task
app = Flask(__name__)

# CRUD
# Create, Read, Update and Delete = Criar, Ler, Atualizar, Deletar
# Tabela: Tarefa

@app.route('/')
def hello_world():
  return "Hello World" 
if __name__ == "__main__":
  app.run(debug=True)