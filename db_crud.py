import sqlite3
import hashlib 
from datetime import datetime
import os

NOME_DB = 'otaku_list.db' 
STATUS_VALIDOS = ("Assistindo", "Concluído", "Planejo Assistir", "Abandonado", "Pausado") 

# --- 1. SETUP: CRIAÇÃO DE TABELAS ---
def criar_tabelas_otaku_list():
    """Cria o arquivo DB e todas as tabelas (Se não existirem)."""
    conn = None
    try:
        conn = sqlite3.connect(NOME_DB)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;") 

        # Tabela 1: Usuario
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Usuario (
                idUsuario INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL,
                dataCadastro TEXT NOT NULL
            );
        """)

        # Tabela 2: Anime
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Anime (
                idAnime INTEGER PRIMARY KEY,
                titulo TEXT NOT NULL,
                genero TEXT,
                anoLancamento INTEGER,
                plataforma TEXT,
                sinopse TEXT
            );
        """)

        # Tabela 3: ListaUsuario (Relacionamento N:N com status pessoal)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ListaUsuario (
                idUsuario INTEGER NOT NULL,
                idAnime INTEGER NOT NULL,
                status TEXT NOT NULL,
                notasPessoais TEXT,
                dataInclusao TEXT NOT NULL,
                PRIMARY KEY (idUsuario, idAnime),
                FOREIGN KEY (idUsuario) REFERENCES Usuario(idUsuario) ON DELETE CASCADE,
                FOREIGN KEY (idAnime) REFERENCES Anime(idAnime) ON DELETE CASCADE
            );
        """)

        # Tabela 4: Avaliacao
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Avaliacao (
                idAvaliacao INTEGER PRIMARY KEY AUTOINCREMENT,
                idUsuario INTEGER NOT NULL,
                idAnime INTEGER NOT NULL,
                nota INTEGER NOT NULL,
                comentario TEXT,
                dataAvaliacao TEXT NOT NULL,
                FOREIGN KEY (idUsuario) REFERENCES Usuario(idUsuario) ON DELETE CASCADE,
                FOREIGN KEY (idAnime) REFERENCES Anime(idAnime) ON DELETE CASCADE
            );
        """)
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao criar tabelas: {e}")
    finally:
        if conn:
            conn.close()


# --- 2. SEGURANÇA E AUTENTICAÇÃO (RF 02, RF 01) ---

def criptografar_senha(senha):
    """Retorna o hash SHA-256 da senha."""
    return hashlib.sha256(senha.encode()).hexdigest()

def cadastrar_usuario(nome, email, senha):
    conn = None
    try:
        conn = sqlite3.connect(NOME_DB)
        cursor = conn.cursor()
        senha_criptografada = criptografar_senha(senha)
        data_cadastro = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        sql_insert = """
            INSERT INTO Usuario (nome, email, senha, dataCadastro)
            VALUES (?, ?, ?, ?)
        """
        # 💡 MENSAGEM DE SUCESSO NO TERMINAL (1)
        print(f"\n[BD] Tentando cadastrar: {email}") 
        
        cursor.execute(sql_insert, (nome, email, senha_criptografada, data_cadastro))
        
        conn.commit()  # <-- Salvando a transação!
        
        id_criado = cursor.lastrowid
        # 💡 MENSAGEM DE CONFIRMAÇÃO FINAL (2)
        print(f"[BD] USUÁRIO CADASTRADO com ID: {id_criado}")
        
        return id_criado

    except sqlite3.IntegrityError:
        # Se o email já existir (UNIQUE)
        print(f"[BD] ERRO INTEGRIDADE: Email {email} já existe.")
        return None
    except Exception as e:
        # Erro geral (para pegar qualquer erro não mapeado)
        print(f"[BD] ERRO FATAL ao cadastrar: {e}") 
        return None
    finally:
        if conn: conn.close()

def fazer_login(email, senha):
    conn = None
    try:
        conn = sqlite3.connect(NOME_DB)
        cursor = conn.cursor()
        sql_select = "SELECT idUsuario, nome, senha FROM Usuario WHERE email = ?;"
        cursor.execute(sql_select, (email,))
        usuario = cursor.fetchone() 
        if usuario is None: return None, "Usuário não encontrado."
        
        id_usuario, nome_usuario, senha_hash_armazenada = usuario
        senha_hash_fornecida = criptografar_senha(senha)

        if senha_hash_fornecida == senha_hash_armazenada:
            return {'id': id_usuario, 'nome': nome_usuario}, "Login bem-sucedido."
        else:
            return None, "Senha incorreta."
    except sqlite3.Error as e:
        print(f"Erro ao tentar fazer login: {e}")
        return None, "Erro interno do sistema."
    finally:
        if conn: conn.close()


# --- 3. GERENCIAMENTO DE LISTAS (RF 04, RF 06, RF 07) ---

def adicionar_metadados_anime(id_anime, titulo, genero, ano, plataforma, sinopse):
    """Insere dados básicos de um anime na tabela 'Anime'."""
    conn = None
    try:
        conn = sqlite3.connect(NOME_DB)
        cursor = conn.cursor()
        sql_insert = """
            INSERT OR IGNORE INTO Anime 
            (idAnime, titulo, genero, anoLancamento, plataforma, sinopse)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql_insert, (id_anime, titulo, genero, ano, plataforma, sinopse))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao adicionar metadados do anime: {e}")
        return False
    finally:
        if conn: conn.close()

def adicionar_anime_lista_usuario(id_usuario, id_anime, status, notas_pessoais=None):
    """RF 04: Adiciona/Atualiza um anime à lista pessoal do usuário."""
    if status not in STATUS_VALIDOS:
        return False, f"Status inválido. Use um destes: {', '.join(STATUS_VALIDOS)}"

    conn = None
    try:
        conn = sqlite3.connect(NOME_DB)
        cursor = conn.cursor()
        data_inclusao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        sql_insert_or_replace = """
            INSERT OR REPLACE INTO ListaUsuario 
            (idUsuario, idAnime, status, notasPessoais, dataInclusao)
            VALUES (?, ?, ?, ?, ?)
        """
        cursor.execute(sql_insert_or_replace, (id_usuario, id_anime, status, notas_pessoais, data_inclusao))
        
        conn.commit()
        return True, "Anime adicionado/atualizado na lista com sucesso!"
    except sqlite3.IntegrityError:
        return False, "Usuário ou Anime ID não existe."
    except sqlite3.Error as e:
        return False, "Erro interno ao adicionar à lista."
    finally:
        if conn: conn.close()

def listar_animes_por_status(id_usuario, status):
    """RF 06: Exibe a lista de animes do usuário, organizada por status."""
    conn = None
    try:
        conn = sqlite3.connect(NOME_DB)
        cursor = conn.cursor()
        sql_select = """
            SELECT T1.titulo, T1.genero, T1.anoLancamento, T2.status, T2.notasPessoais, T2.dataInclusao, T1.idAnime
            FROM Anime T1
            INNER JOIN ListaUsuario T2 ON T1.idAnime = T2.idAnime
            WHERE T2.idUsuario = ? AND T2.status = ?
            ORDER BY T2.dataInclusao DESC;
        """
        cursor.execute(sql_select, (id_usuario, status))
        animes = cursor.fetchall()
        lista_formatada = []
        for anime in animes:
            lista_formatada.append({
                'titulo': anime[0], 'genero': anime[1], 'ano': anime[2], 'status': anime[3], 
                'notas': anime[4], 'data_add': anime[5], 'id_anime': anime[6]
            })
        return lista_formatada
    except sqlite3.Error as e:
        print(f"Erro ao listar animes: {e}")
        return []
    finally:
        if conn: conn.close()

def excluir_anime_lista(id_usuario, id_anime):
    """RF 07: Permite a exclusão de um anime da lista do usuário."""
    conn = None
    try:
        conn = sqlite3.connect(NOME_DB)
        cursor = conn.cursor()
        sql_delete = "DELETE FROM ListaUsuario WHERE idUsuario = ? AND idAnime = ?;"
        cursor.execute(sql_delete, (id_usuario, id_anime))
        
        if cursor.rowcount > 0:
            conn.commit()
            return True, "Anime excluído com sucesso."
        else:
            return False, "Anime não encontrado na sua lista."
    except sqlite3.Error as e:
        return False, "Erro interno ao excluir anime."
    finally:
        if conn: conn.close()

# --- DEMONSTRAÇÃO E TESTES ---
# Remova esta função do seu db_crud.py quando for para Produção.
def demonstrar_integracao():
    criar_tabelas_otaku_list() # Garante a estrutura
    # ... (restante da lógica de demonstração/teste) ...

if __name__ == '__main__':
    # Esta é a única linha que deve estar aqui para testes. 
    # Mantenha-a como está para testar o db_crud.py diretamente.
    # demonstrar_integracao() # Descomente para rodar testes manuais do DB
    pass

def atualizar_perfil_usuario(id_usuario, novo_nome):
    """Atualiza o nome do usuário na tabela Usuario."""
    conn = None
    try:
        conn = sqlite3.connect(NOME_DB)
        cursor = conn.cursor()
        
        sql_update = """
            UPDATE Usuario 
            SET nome = ? 
            WHERE idUsuario = ?;
        """
        cursor.execute(sql_update, (novo_nome, id_usuario))
        conn.commit()
        
        if cursor.rowcount > 0:
            return True, "Nome do perfil atualizado com sucesso."
        else:
            return False, "Usuário não encontrado."
            
    except sqlite3.Error as e:
        print(f"Erro ao atualizar perfil: {e}")
        return False, "Erro interno ao atualizar perfil."
    finally:
        if conn: conn.close()