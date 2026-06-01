# ==============================================================================
# 1. IMPORTAÇÕES
# ==============================================================================
import os
import sqlite3
from flask import Flask, render_template, jsonify, g
from flask_cors import CORS

# Tenta importar psycopg2 (PostgreSQL). Se não estiver instalado, ignora.
try:
    import psycopg2
    import psycopg2.extras
    PSYCOPG2_AVAILABLE = True
except Exception as e:
    print("ERRO PSYCOPG2:", e)
    PSYCOPG2_AVAILABLE = False

# ==============================================================================
# 2. CONFIGURAÇÃO DA APLICAÇÃO
# ==============================================================================
app = Flask(__name__)
CORS(app)

DATABASE_URL = os.environ.get('DATABASE_URL')
print("DATABASE_URL existe?", bool(DATABASE_URL))
print("PSYCOPG2_AVAILABLE =", PSYCOPG2_AVAILABLE)

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

USANDO_POSTGRES = bool(DATABASE_URL and PSYCOPG2_AVAILABLE)
DATABASE_LOCAL  = 'banco_local.db'

# Placeholder de query: '?' para SQLite, '%s' para PostgreSQL
PH = '%s' if USANDO_POSTGRES else '?'

print(f"[DB] Modo: {'PostgreSQL (Render)' if USANDO_POSTGRES else 'SQLite (Local)'}")

# ==============================================================================
# 3. GERENCIAMENTO DA CONEXÃO COM O BANCO
# ==============================================================================
def get_db():
    """
    Retorna a conexão ativa com o banco de dados.
    Reutiliza a mesma conexão durante toda a requisição (padrão Flask com 'g').
    """
    db = getattr(g, '_database', None)
    if db is None:
        if USANDO_POSTGRES:
            db = psycopg2.connect(DATABASE_URL)
        else:
            db = sqlite3.connect(DATABASE_LOCAL)
            db.row_factory = sqlite3.Row
        g._database = db
    return db


def get_cursor(db):
    """Retorna o cursor correto para cada banco."""
    if USANDO_POSTGRES:
        return db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    else:
        return db.cursor()


@app.teardown_appcontext
def close_connection(exception):
    """Fecha a conexão ao fim de cada requisição."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# ==============================================================================
# 4. ROTA DO FRONT-END
# ==============================================================================
@app.route('/')
def index():
    return render_template('index.html')

# ==============================================================================
# 5. ROTAS DA API
# ==============================================================================

@app.route('/api/eventos', methods=['GET'])
def get_eventos_basicos():
    """
    ROTA 1 — LAZY LOADING (Carga Leve)
    Retorna apenas os dados necessários para renderizar os cards da timeline.
    """
    try:
        db  = get_db()
        cur = get_cursor(db)
        cur.execute("""
            SELECT id, titulo, data_evento, resumo_timeline
            FROM acontecimentos
            ORDER BY data_evento ASC
        """)
        rows = cur.fetchall()

        resultado = []
        for row in rows:
            d_row = dict(row)
            if hasattr(d_row['data_evento'], 'strftime'):
                d_row['data_evento'] = d_row['data_evento'].strftime('%Y-%m-%d')
            else:
                d_row['data_evento'] = str(d_row['data_evento'])
            resultado.append(d_row)

        return jsonify(resultado), 200

    except Exception as e:
        app.logger.error(f"[ERRO /api/eventos] {e}")
        return jsonify({"erro": "Falha ao buscar eventos.", "detalhe": str(e)}), 500


@app.route('/api/evento/<int:evento_id>', methods=['GET'])
def get_detalhes_evento(evento_id):
    """
    ROTA 2 — DETALHE COMPLETO (Chamada sob demanda / Lazy Loading)
    Inclui definicao_profunda e o JOIN N:M com personagens.
    CONTRATO COM main.js: o JSON retornado deve conter as chaves
      'definicao_profunda' e 'personagens' (lista).
    """
    try:
        db  = get_db()
        cur = get_cursor(db)

        cur.execute(
            f"SELECT * FROM acontecimentos WHERE id = {PH}",
            (evento_id,)
        )
        evento_row = cur.fetchone()

        if evento_row is None:
            return jsonify({"erro": f"Evento com id={evento_id} não encontrado."}), 404

        evento_detalhado = dict(evento_row)

        if hasattr(evento_detalhado['data_evento'], 'strftime'):
            evento_detalhado['data_evento'] = evento_detalhado['data_evento'].strftime('%Y-%m-%d')
        else:
            evento_detalhado['data_evento'] = str(evento_detalhado['data_evento'])

        # JOIN N:M — personagens vinculados a este acontecimento
        cur.execute(
            f"""
            SELECT
                p.nome,
                p.nacionalidade,
                pt.papel_historico
            FROM personagens p
            JOIN participacao pt ON p.id = pt.personagem_id
            WHERE pt.acontecimento_id = {PH}
            ORDER BY p.nome ASC
            """,
            (evento_id,)
        )
        personagens_rows = cur.fetchall()
        evento_detalhado['personagens'] = [dict(p) for p in personagens_rows]

        return jsonify(evento_detalhado), 200

    except Exception as e:
        app.logger.error(f"[ERRO /api/evento/{evento_id}] {e}")
        return jsonify({"erro": "Falha ao buscar detalhes do evento.", "detalhe": str(e)}), 500


@app.route('/api/personagem/<int:personagem_id>', methods=['GET'])
def get_personagem(personagem_id):
    """
    ROTA 3 — PERFIL DO PERSONAGEM
    Retorna dados do personagem + todos os eventos em que participou (N:M inverso).
    """
    try:
        db  = get_db()
        cur = get_cursor(db)

        cur.execute(
            f"SELECT * FROM personagens WHERE id = {PH}",
            (personagem_id,)
        )
        personagem_row = cur.fetchone()

        if personagem_row is None:
            return jsonify({"erro": f"Personagem com id={personagem_id} não encontrado."}), 404

        personagem = dict(personagem_row)

        cur.execute(
            f"""
            SELECT
                a.id            AS evento_id,
                a.titulo,
                a.data_evento,
                a.resumo_timeline,
                pt.papel_historico
            FROM acontecimentos a
            JOIN participacao pt ON a.id = pt.acontecimento_id
            WHERE pt.personagem_id = {PH}
            ORDER BY a.data_evento ASC
            """,
            (personagem_id,)
        )
        eventos = cur.fetchall()

        lista_eventos = []
        for e in eventos:
            d_e = dict(e)
            if hasattr(d_e['data_evento'], 'strftime'):
                d_e['data_evento'] = d_e['data_evento'].strftime('%Y-%m-%d')
            else:
                d_e['data_evento'] = str(d_e['data_evento'])
            lista_eventos.append(d_e)

        personagem['eventos_participados'] = lista_eventos

        return jsonify(personagem), 200

    except Exception as e:
        app.logger.error(f"[ERRO /api/personagem/{personagem_id}] {e}")
        return jsonify({"erro": "Falha ao buscar personagem.", "detalhe": str(e)}), 500

# ==============================================================================
# 6. INICIALIZAÇÃO LOCAL
# ==============================================================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)