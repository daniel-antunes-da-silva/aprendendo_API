from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Criar uma API flask
app = Flask(__name__)
# Criar uma instância de SQLAlchemy
app.config['SECRET_KEY'] = 'abcdef123456'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'



db = SQLAlchemy(app)
db: SQLAlchemy
# Definir a estrutura da tabela Postagem
# Toda postagem deve ter: id_postagem, titulo, autor
# Abaixo está sendo criado.


class Postagem(db.Model):
    __tablename__ = 'postagem'
    id_postagem = db.Column(db.Integer, primary_key=True)
    # O nome que se dá à variável, se tornará o nome da coluna em si.
    titulo = db.Column(db.String)
    id_autor = db.Column(db.Integer, db.ForeignKey('autor.id_autor'))


# Definir a estrutura da tabela Autor
# id_autor, nome, e-mail, senha, admin, postagens (realizadas pelo autor).


class Autor(db.Model):
    __tablename__ = 'autor'
    id_autor = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String)
    email = db.Column(db.String)
    senha = db.Column(db.String)
    admin = db.Column(db.Boolean)
    postagens = db.relationship('Postagem')


def inicializar_banco():
    with app.app_context():
        # Executar comando para criar banco de dados
        db.drop_all()
        db.create_all()
        # Criar usuários administradores
        autor = Autor(nome='daniel', email='daniel.antunes.nutri@gmail.com',
                      senha='123456', admin=True)
        db.session.add(autor)
        db.session.commit()


if __name__ == '__main__':
    inicializar_banco()
