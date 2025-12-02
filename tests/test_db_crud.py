import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from db_crud import (
    criar_tabelas_otaku_list,
    cadastrar_usuario,
    fazer_login,
    adicionar_anime_lista_usuario,
    listar_animes_por_status,
    excluir_anime_lista,
    atualizar_perfil_usuario
)
import os


@pytest.fixture
def setup_db():
    # Remove banco anterior
    if os.path.exists("otaku_list.db"):
        os.remove("otaku_list.db")

    # Cria as tabelas
    criar_tabelas_otaku_list()

    yield

    # Remove banco após testes
    if os.path.exists("otaku_list.db"):
        os.remove("otaku_list.db")


def test_cadastro_usuario(setup_db):
    novo_id = cadastrar_usuario("Gabriel", "teste@example.com", "123456")
    assert isinstance(novo_id, int)
    assert novo_id > 0


def test_login_sucesso(setup_db):
    cadastrar_usuario("Teste", "login@example.com", "senha123")
    user, msg = fazer_login("login@example.com", "senha123")
    assert user is not None
    assert msg == "Login bem-sucedido."


def test_login_falha(setup_db):
    cadastrar_usuario("Teste", "login2@example.com", "senha123")
    user, msg = fazer_login("login2@example.com", "errada")
    assert user is None
    assert msg == "Senha incorreta."
