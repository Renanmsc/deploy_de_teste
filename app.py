import os
from flask import Flask, request
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import socket, ssl


app = Flask(__name__)

# Carrega as variáveis de ambiente do arquivo .cred (se disponível)
load_dotenv('.cred')

# Configurações para conexão com o banco de dados usando variáveis de ambiente
config = {
    'host': os.getenv('DB_HOST', 'localhost'),  # Obtém o host do banco de dados da variável de ambiente
    'user': os.getenv('DB_USER'),  # Obtém o usuário do banco de dados da variável de ambiente
    'password': os.getenv('DB_PASSWORD'),  # Obtém a senha do banco de dados da variável de ambiente
    'database': os.getenv('DB_NAME', 'db_escola'),  # Obtém o nome do banco de dados da variável de ambiente
    'port': int(os.getenv('DB_PORT', 3306)),  # Obtém a porta do banco de dados da variável de ambiente
    'ssl_ca': os.getenv('SSL_CA_PATH'),  # Caminho para o certificado SSL
    'ssl_verify_cert': True
}

# Função para conectar ao banco de dados
def connect_db():
    """Estabelece a conexão com o banco de dados usando as configurações fornecidas."""
    try:
        # Tenta estabelecer a conexão com o banco de dados usando mysql-connector-python
        conn = mysql.connector.connect(**config)
        if conn.is_connected():
            return conn
    except Error as err:
        # Em caso de erro, imprime a mensagem de erro
        print(f"Erro: {err}")
        return None
    


# Função para inserir um novo aluno
@app.route('/aluno', methods=['POST']) 
def post_aluno():
    success = False

    data = request.json
    
    campos_obrigatorios = ['nome', 'cpf']
    for campo in campos_obrigatorios:
        if campo not in data:
            resp = {"erro:" f"Campo obrigatório {campo} não informado"}
            return resp, 400
        
    idade = data.get('idade', 0)
    # if 'nome' not in data or 'cpf' not in data:
        # return "Erro ao cadastrar aluno, faltam informações", 400
    """Insere um novo aluno na tabela tbl_alunos e retorna o ID do aluno inserido."""
    conn = connect_db()  # Conecta ao banco de dados
    aluno_id = None  # ID do aluno inserido
    if conn and conn.is_connected():
        try:
            cursor = conn.cursor()  # Cria um cursor para executar comandos SQL
            sql = "INSERT INTO tbl_alunos (nome, cpf, idade) VALUES (%s, %s, %s)"  # Comando SQL para inserir um aluno
            values = (data['nome'], data['cpf'], idade)  # Dados a serem inseridos

            # Executa o comando SQL com os valores fornecidos
            print(f"Executando SQL: {sql} com valores: {values}")
            cursor.execute(sql, values)
            
            # Confirma a transação no banco de dados
            conn.commit()

            # Obtém o ID do registro recém-inserido
            aluno_id = cursor.lastrowid
            success = True
            
        except Error as err:
            # Em caso de erro na inserção, imprime a mensagem de erro
            error = str(err)
        finally:
            # Fecha o cursor e a conexão para liberar recursos
            cursor.close()
            conn.close()
    if success:
        resp = {'id': aluno_id, 'nome': data['nome'], 'cpf': data['cpf'], 'idade': idade}
        return resp, 201
    resp = {"erro": "Erro ao inserir aluno", "message": error}
    return resp, 500

@app.route('/aluno', methods=['GET'])
def get_alunos():

    # conectar com a base
    conn = connect_db()

    if conn is None:
        resp = {"erro": "Erro ao conectar ao banco de dados"}
        return resp, 500
    
    # se chegou até, tenho uma conexão válida
    cursor = conn.cursor()

    sql = "SELECT * from tbl_alunos"
    cursor.execute(sql)

    results = cursor.fetchall()
    if not results:
        resp = {"erro": "Nenhum aluno encontrado"}
        return resp, 404
    else:
        alunos = []
        for aluno in results:
            aluno_dict = {
                "id": aluno[0],
                "nome": aluno[1],
                "cpf": aluno[2]
            }
            alunos.append(aluno_dict)

        resp = {"alunos": alunos}
        return resp, 200



if __name__ == '__main__':
    app.run(debug=True)
