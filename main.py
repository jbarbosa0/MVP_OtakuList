

from flask import Flask

from db_crud import criar_tabelas_otaku_list 

app = Flask(__name__)

app.secret_key = 'sua_chave_secreta_e_segura' 

from routes import * 

if __name__ == '__main__':
    print("--- INICIALIZAÇÃO DO SERVIDOR OTALKULIST ---")
    
    
    criar_tabelas_otaku_list() 
    print("Banco de dados verificado e pronto.")

    
    app.run(debug=True, host='0.0.0.0', port=5000)
