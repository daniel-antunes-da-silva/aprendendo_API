from flask import Flask, jsonify, request, make_response
from estrutura_banco_de_dados import Autor, Postagem, app, db
import json
from datetime import datetime, timedelta
from functools import wraps
import os
import jwt

# Criando token para sempre que precisar proteger alguma requisição.
# Para isso, basta colocar o @token_obrigatorio debaixo das rotas que queremos proteger.
# É necessário, também, colocar o parâmetro (nesse caso, autor) como primário nas funções que protegemos.
def token_obrigatorio(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Verificar se um token foi enviado
        if 'x-acess-token' in request.headers:
            token = request.headers['x-acess-token']
        if not token:
            return jsonify({'mensagem': 'token não foi incluído'}, 401)
        # Se temos um token, validar acesso consultando o BD.
        try:
            resultado = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            autor = Autor.query.filter_by(id_autor=resultado['id_autor']).first()
        except:
            return jsonify({'mensagem': 'token é invalido'}, 401)
        return f(autor, *args, *kwargs)
    return decorated

@app.route('/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório"'})
    usuario = Autor.query.filter_by(nome=auth.username).first()
    if not usuario:
        return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório"'})
    if auth.password == usuario.senha:
        token = jwt.encode({'id_autor': usuario.id_autor, 'exp': datetime.utcnow() + timedelta(minutes=30)},
                           app.config['SECRET_KEY'])
        return jsonify({'token': token})
    return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório"'})


# ROTA PADRÃO - get http://localhost:5000
@app.route('/')
@token_obrigatorio
def obter_postagens(autor):
    # está buscando todas as postagens existentes no banco de dados e armazenando-as em uma lista chamada postagens.
    # Após essa linha de código, você pode usar a lista postagens para manipular ou exibir as postagens de alguma forma.
    postagens = Postagem.query.all()
    lista_de_postagens = []
    for postagem in postagens:
        postagem_atual = {}
        postagem_atual['titulo'] = postagem.titulo
        postagem_atual['id_autor'] = postagem.id_autor
        lista_de_postagens.append(postagem_atual)
    return jsonify({'postagens': lista_de_postagens})


# Get com ID - get http://localhost:5000/postagem/1 <- nº do ID.
@app.route('/postagem/<int:id_postagem>', methods=['GET'])
@token_obrigatorio
def obter_postagem_por_indice(autor, id_postagem):
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()
    if not postagem:
        return jsonify('Postagem não encontrada.')
    postagem_atual = {}
    postagem_atual['id_autor'] = postagem.id_autor
    postagem_atual['titulo'] = postagem.titulo
    return {'postagem': postagem_atual}


# Criar uma nova postagem - POST http://localhost:5000/postagem
@app.route('/postagem/', methods=['POST'])
@token_obrigatorio
def nova_postagem(autor):
    nova_postagem = request.get_json()
    postagem = Postagem(
        titulo=nova_postagem['titulo'], id_autor=nova_postagem['id_autor'])
    db.session.add(postagem)
    db.session.commit()

    return jsonify('Postagem criada com sucesso!')


# Alterar uma postagem existente - PUT
@app.route('/postagem/<int:id_postagem>', methods=['PUT'])
@token_obrigatorio
def alterar_postagem(autor, id_postagem):
    postagem_a_alterar = request.get_json()
    postagem = Postagem.query.filter_by(
        id_postagem=id_postagem).first()
    if not postagem:
        return jsonify('Postagem não encontrada.')
    try:
        postagem.titulo = postagem_a_alterar['titulo']
    except:
        pass
    try:
        postagem.id_autor = postagem_a_alterar['id_autor']
    except:
        pass
    return jsonify({'mensagem': 'postagem alterada com sucesso.'})


# Excluir uma postagem - DELETE
@app.route('/postagem/<int:id_postagem>', methods=['DELETE'])
@token_obrigatorio
def deletar_postagem(autor, id_postagem):
    postagem_existente = Postagem.query.filter_by(id_postagem=id_postagem).first()
    if not postagem_existente:
        return jsonify('Postagem não encontrada.')
    db.session.delete(postagem_existente)
    db.session.commit()
    return jsonify({'mensagem': 'postagem excluída com sucesso.'})


@app.route('/autores/')
@token_obrigatorio
def obter_autores(autor):
    autores = Autor.query.all()
    lista_de_autores = []
    for autor in autores:
        autor_atual = {}
        autor_atual['id_autor'] = autor.id_autor
        autor_atual['nome'] = autor.nome
        autor_atual['email'] = autor.email
        lista_de_autores.append(autor_atual)
    return jsonify({'autores': lista_de_autores})


@app.route('/autores/<int:id_autor>', methods=['GET'])
@token_obrigatorio
def obter_autor_por_id(autor, id_autor):
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor:
        return jsonify('Autor não encontrado.')
    autor_atual = {}
    autor_atual['id_autor'] = autor.id_autor
    autor_atual['nome'] = autor.nome
    autor_atual['email'] = autor.email

    # return jsonify(f'Você buscou pelo autor {autor_atual}')
    return jsonify({'autor': autor_atual})


@app.route('/autores', methods=['POST'])
@token_obrigatorio
def novo_autor(autor):
    novo_autor = request.get_json()
    autor = Autor(nome=novo_autor['nome'], senha=novo_autor['senha'],
                  email=novo_autor['email'])
    # para acrescentar esse autor ao banco de dados
    db.session.add(autor)
    db.session.commit()

    return jsonify({'mensagem': 'usuário criado com sucesso'}, 200)


@app.route('/autores/<int:id_autor>', methods=['PUT'])
@token_obrigatorio
def alterar_autor(autor, id_autor):
    usuario_a_alterar = request.get_json()
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor:
        return jsonify('Autor não encontrado.')
    try:
        autor.nome = usuario_a_alterar['nome']
    except:
        pass
    try:
        autor.email = usuario_a_alterar['email']
    except:
        pass
    try:
        autor.senha = usuario_a_alterar['senha']
    except:
        pass

    db.session.commit()
    return jsonify(f'usuário alterado com sucesso!')


@app.route('/autores/<int:id_autor>', methods=['DELETE'])
@token_obrigatorio
def excluir_autor(autor, id_autor):
    autor_existente = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor_existente:
        return jsonify('Este autor não foi encontrado!')
    db.session.delete(autor_existente)
    db.session.commit()

    return jsonify({'mensagem': 'Autor excluído com sucesso!'})


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
