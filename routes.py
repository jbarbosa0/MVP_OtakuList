from flask import render_template, request, redirect, session, url_for, jsonify
from db_crud import adicionar_metadados_anime, fazer_login, cadastrar_usuario, adicionar_anime_lista_usuario, listar_animes_por_status, excluir_anime_lista
from main import app
from anilist_api import (
    get_popular_animes,
    get_trending_animes,
    get_seasonal_animes,
    get_all_animes
)

def template_vars(**kwargs):
    
    user_session = session.get('usuario')
    is_logged = ('usuario' in session)
    
    return dict(
        usuario=user_session,
        isLogged=is_logged,
        **kwargs
    )



@app.route('/')
def homepage():
    populares = get_popular_animes()
    trends = get_trending_animes()
    temporada = get_seasonal_animes()
    return render_template(
        'homepage.html',
        **template_vars(populares=populares, trends=trends, temporada=temporada)
    )

@app.route('/animes')
def all_animes():
    animes = get_all_animes()
    return render_template(
        'animes.html',
        **template_vars(animes=animes)
    )

@app.route('/cadastro')
def cadastro_page():
    return render_template('cadastro.html', **template_vars())
    
@app.route('/login')
def login_page():
    
    return render_template('login.html', **template_vars())



@app.route('/cadastro', methods=['POST'])
def cadastro_action():
   
    print("\n[FLASK] Recebendo submissão de cadastro...") 
    
    
    nome = request.form.get('nome') 
    email = request.form.get('email')
    senha = request.form.get('senha')
    
    
    if not nome or not email or not senha:
        print("[FLASK] ERRO: Dados incompletos ou nome de campo incorreto no HTML.")
        return redirect(url_for('cadastro_page'))

    
    
  
    id_novo_usuario = cadastrar_usuario(nome, email, senha)

    if id_novo_usuario:
       
        print("[FLASK] Redirecionando para login após sucesso.")
        return redirect(url_for('login_page'))
    else:
        
        print("[FLASK] Cadastro falhou (E-mail duplicado ou erro interno).")
        return redirect(url_for('cadastro_page'))


@app.route('/login', methods=['POST'])
def login_action():
    email = request.form['email']
    senha = request.form['senha']

    
    usuario_db, mensagem = fazer_login(email, senha) 

    if usuario_db:
        
        session['usuario'] = {
            "id": usuario_db['id'],      
            "email": email, 
            "nome": usuario_db['nome']
        }
        return redirect(url_for('profile'))

    
    return redirect(url_for('login_page')) 



@app.route('/perfil')
def profile():
    if 'usuario' not in session:
        
        return redirect(url_for('login_page')) 
    return render_template('perfil.html', **template_vars())

@app.route('/minha-lista')
def my_list():
    
    return render_template(
        'minha-lista.html',
       
        **template_vars() 
    )


@app.route('/logout')
def logout():
    session.clear()
    
    return redirect(url_for('homepage'))




@app.route('/api/list/<status>', methods=['GET'])
def api_list_animes(status):
    
    if 'usuario' not in session:
        return jsonify({"success": False, "message": "Usuário não autenticado."}), 401
    
    id_usuario = session['usuario']['id']
    
    
    lista = listar_animes_por_status(id_usuario, status)

    return jsonify({
        "success": True,
        "animes": lista
    }), 200

@app.route('/api/add_anime', methods=['POST'])
def api_add_anime():
    
    data = request.get_json() 
    
    if 'usuario' not in session:
        return jsonify({"success": False, "message": "Usuário não autenticado."}), 401
    
    id_usuario = session['usuario']['id'] 
    id_anime = data.get('id_anime')
    status = data.get('status')
    notas = data.get('notas')
    
    if not id_anime or not status:
        return jsonify({"success": False, "message": "ID do Anime e Status são obrigatórios."}), 400

    
    adicionar_metadados_anime(
        id_anime=id_anime, 
        titulo=data.get('titulo_anime', f"Anime ID {id_anime}"), 
        genero=data.get('genero', 'N/A'), 
        ano=data.get('ano', 0), 
        plataforma=data.get('plataforma', 'N/A'),
        sinopse=data.get('sinopse', '')
    )

    sucesso, mensagem = adicionar_anime_lista_usuario(
        id_usuario=id_usuario, 
        id_anime=id_anime, 
        status=status, 
        notas_pessoais=notas
    )

    if sucesso:
        return jsonify({"success": True, "message": mensagem}), 200
    else:
        return jsonify({"success": False, "message": mensagem}), 400
    
@app.route('/api/perfil/atualizar', methods=['POST'])
def api_atualizar_perfil():
    
    data = request.get_json() 
    
    if 'usuario' not in session:
        return jsonify({"success": False, "message": "Usuário não autenticado."}), 401
    
    id_usuario = session['usuario']['id']
    novo_nome = data.get('nome') 

    if not novo_nome:
        return jsonify({"success": False, "message": "O novo nome é obrigatório."}), 400

    sucesso, mensagem = atualizar_perfil_usuario(id_usuario, novo_nome)

    if sucesso:
        
        session['usuario']['nome'] = novo_nome
        return jsonify({"success": True, "message": mensagem, "novo_nome": novo_nome}), 200
    else:
        return jsonify({"success": False, "message": mensagem}), 400
