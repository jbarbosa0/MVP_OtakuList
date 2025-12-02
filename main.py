# main.py (Versão Corrigida)

from flask import Flask
# 💡 Você precisa importar a função de inicialização do BD do seu db_crud.py
# (Se não estiver, o servidor vai ligar, mas o banco não será criado!)
from db_crud import criar_tabelas_otaku_list 

app = Flask(__name__)
# ⚠️ Chave secreta necessária para usar 'session' no routes.py
app.secret_key = 'sua_chave_secreta_e_segura' 

from routes import * # Importa todas as rotas

if __name__ == '__main__':
    print("--- INICIALIZAÇÃO DO SERVIDOR OTALKULIST ---")
    
    # 1. PREPARAÇÃO DO BANCO DE DADOS: 
    criar_tabelas_otaku_list() 
    print("Banco de dados verificado e pronto.")

    # 2. INICIA O SERVIDOR FLASK:
    app.run(debug=True, host='0.0.0.0', port=5000)