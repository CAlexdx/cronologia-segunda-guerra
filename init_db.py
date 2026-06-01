# ==============================================================================
# SCRIPT DE INICIALIZAÇÃO E POPULAÇÃO DO BANCO DE DADOS (SQLite / PostgreSQL)
# Baseado nas anotações de aula: Da Marcha sobre Roma à Rendição do Japão
# Execute uma vez com: python init_db.py
# ==============================================================================

import os
import sqlite3

# Tenta importar psycopg2 (PostgreSQL). Se não estiver instalado, ignora.
try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

# DETECÇÃO DE AMBIENTE (Render x Local)
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

USANDO_POSTGRES = bool(DATABASE_URL and PSYCOPG2_AVAILABLE)
DATABASE_LOCAL  = 'banco_local.db'

def conectar_banco():
    """Cria a conexão de acordo com o ambiente."""
    if USANDO_POSTGRES:
        print("[INIT] Conectando ao PostgreSQL (Render)...")
        return psycopg2.connect(DATABASE_URL)
    else:
        print(f"[INIT] Conectando ao SQLite Local ({DATABASE_LOCAL})...")
        return sqlite3.connect(DATABASE_LOCAL)

def inicializar_e_popular():
    conn   = conectar_banco()
    cursor = conn.cursor()
    ph     = "%s" if USANDO_POSTGRES else "?"

    # 1. REMOÇÃO DAS TABELAS (evita duplicação ao rodar o script várias vezes)
    print("[INIT] Limpando tabelas antigas se existirem...")
    if USANDO_POSTGRES:
        cursor.execute("DROP TABLE IF EXISTS participacao CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS personagens CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS acontecimentos CASCADE;")
    else:
        cursor.execute("DROP TABLE IF EXISTS participacao;")
        cursor.execute("DROP TABLE IF EXISTS personagens;")
        cursor.execute("DROP TABLE IF EXISTS acontecimentos;")

    # 2. CRIAÇÃO DAS TABELAS
    # ATENÇÃO: o nome 'definicao_profunda' é o contrato com app.py e main.js.
    # main.js lê data.definicao_profunda → app.py faz SELECT * → coluna deve
    # se chamar exatamente 'definicao_profunda' nas três camadas.
    print("[INIT] Criando tabelas...")

    if USANDO_POSTGRES:
        cursor.execute("""
            CREATE TABLE acontecimentos (
                id                 SERIAL PRIMARY KEY,
                titulo             VARCHAR(200) NOT NULL,
                data_evento        DATE         NOT NULL,
                resumo_timeline    TEXT         NOT NULL,
                definicao_profunda TEXT         NOT NULL,
                imagem_url         TEXT
            );
        """)
        cursor.execute("""
            CREATE TABLE personagens (
                id              SERIAL PRIMARY KEY,
                nome            VARCHAR(200) NOT NULL,
                nacionalidade   VARCHAR(100) NOT NULL,
                biografia_curta TEXT         NOT NULL
            );
        """)
    else:
        cursor.execute("""
            CREATE TABLE acontecimentos (
                id                 INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo             TEXT NOT NULL,
                data_evento        TEXT NOT NULL,
                resumo_timeline    TEXT NOT NULL,
                definicao_profunda TEXT NOT NULL,
                imagem_url         TEXT
            );
        """)
        cursor.execute("""
            CREATE TABLE personagens (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                nome            TEXT NOT NULL,
                nacionalidade   TEXT NOT NULL,
                biografia_curta TEXT NOT NULL
            );
        """)

    # Tabela associativa N:M (igual nos dois bancos)
    cursor.execute("""
        CREATE TABLE participacao (
            acontecimento_id INTEGER NOT NULL,
            personagem_id    INTEGER NOT NULL,
            papel_historico  TEXT    NOT NULL,
            PRIMARY KEY (acontecimento_id, personagem_id),
            FOREIGN KEY (acontecimento_id) REFERENCES acontecimentos(id) ON DELETE CASCADE,
            FOREIGN KEY (personagem_id)    REFERENCES personagens(id)    ON DELETE CASCADE
        );
    """)

    # 3. PERSONAGENS
    # IDs: 1=Mussolini, 2=Hitler, 3=Churchill, 4=De Gaulle,
    #      5=Stalin, 6=Hirohito, 7=Vargas
    print("[INIT] Inserindo Figuras Históricas...")
    personagens_dados = [
        ("Benito Mussolini",           "Itália",           "Líder supremo do Partido Fascista Italiano (Il Duce). Criador do Estado corporativista e totalitário. Suas características principais eram o nacionalismo exacerbado, o militarismo e o anticomunismo."),
        ("Adolf Hitler",               "Alemanha",         "Líder do Partido Nazista (Führer). Implantou uma ditadura baseada no totalitarismo, no antissemitismo e na crença da superioridade da 'Raça Ariana'. Buscava a expansão territorial através do conceito de 'Espaço Vital' (Lebensraum)."),
        ("Winston Churchill",          "Reino Unido",      "Primeiro-Ministro britânico. Principal símbolo da resistência Aliada no Ocidente contra os bombardeios da força aérea alemã e os foguetes V1 e V2 que atingiram Londres."),
        ("Charles de Gaulle",          "França",           "General francês que liderou a 'França Livre'. Recusou a rendição francesa aos alemães e ajudou a organizar a Resistência a partir do seu exílio em Londres."),
        ("Josef Stalin",               "União Soviética",  "Líder da URSS. Firmou inicialmente um pacto de não agressão com Hitler, mas após ser traído, comandou o Exército Vermelho na Frente Oriental, culminando na tomada de Berlim."),
        ("Imperador Showa (Hirohito)", "Japão",            "Líder máximo do Império Japonês, guiou o país por uma política de extremo nacionalismo e militarismo, expandindo seus territórios pela Ásia até o confronto direto com os EUA no Pacífico."),
        ("Getúlio Vargas",             "Brasil",           "Presidente do Brasil durante o Estado Novo. Apesar do seu governo ter características autoritárias internamente, alinhou-se aos Aliados e enviou a Força Expedicionária Brasileira (FEB) para lutar na Europa."),
    ]
    for nome, nac, bio in personagens_dados:
        cursor.execute(
            f"INSERT INTO personagens (nome, nacionalidade, biografia_curta) VALUES ({ph}, {ph}, {ph});",
            (nome, nac, bio)
        )

    # 4. ACONTECIMENTOS
    # IDs sequenciais: 1 a 12
    print("[INIT] Inserindo Linha do Tempo...")
    acontecimentos_dados = [
        (
            "Marcha sobre Roma",
            "1922-10-28",
            "Ascensão do Fascismo na Itália sob o comando de Mussolini.",
            "Fascistas italianos (os 'camisas-negras') marcham sobre a capital, forçando o Rei a entregar o poder a Benito Mussolini. É o marco inicial dos regimes totalitários na Europa, focado no militarismo, unipartidarismo e forte anticomunismo.",
            "https://images.unsplash.com/photo-1543872084-c7bd3822856f?w=600"
        ),
        (
            "Hitler é nomeado Chanceler",
            "1933-01-30",
            "Início oficial do Nazismo e da perseguição na Alemanha.",
            "Hitler assume o poder na Alemanha, marcando o fim da República de Weimar. O Nazismo institui o totalitarismo pleno, com forte censura, propaganda de Estado, antissemitismo e a busca pelo 'Espaço Vital' (Lebensraum) para abrigar a chamada 'Raça Ariana'.",
            "https://images.unsplash.com/photo-1505664194779-8beaceb93744?w=600"
        ),
        (
            "Guernica e a Guerra Civil Espanhola",
            "1937-04-26",
            "O laboratório de testes militares da Alemanha e Itália.",
            "Durante a Guerra Civil Espanhola, as forças aéreas da Alemanha e da Itália bombardeiam a cidade de Guernica. O evento serviu de 'laboratório de testes' para os armamentos do Eixo e táticas de terror contra a população civil que seriam usadas na Segunda Guerra.",
            "https://images.unsplash.com/photo-1440288736878-766fa582b3f5?w=600"
        ),
        (
            "Pacto de Não Agressão",
            "1939-08-23",
            "Alemanha e União Soviética assinam um tratado surpreendente.",
            "Hitler e Stalin assinam o Pacto Molotov-Ribbentrop, prometendo não se atacarem. Secretamente, eles dividem a Polônia entre si, garantindo a Hitler a segurança de não precisar lutar em duas frentes simultâneas no início da guerra.",
            "https://images.unsplash.com/photo-1547658719-da2b81166b58?w=600"
        ),
        (
            "Invasão da Polônia",
            "1939-09-01",
            "O estopim que dá início oficial à Segunda Guerra Mundial.",
            "A Alemanha utiliza a tática da Blitzkrieg (guerra-relâmpago) e invade a Polônia. Em resposta, devido aos tratados de proteção, França e Inglaterra declaram guerra à Alemanha no dia 3 de setembro.",
            "https://images.unsplash.com/photo-1498623116890-37e912163d5d?w=600"
        ),
        (
            "Queda da França",
            "1940-06-14",
            "A França é invadida e dividida pela Alemanha nazista.",
            "Os alemães dominam Paris. A França é dividida: a parte Norte fica sob controle direto dos nazistas, e o Sul transforma-se na 'República de Vichy', um governo fantoche aliado a Hitler. O General De Gaulle foge para comandar a resistência.",
            "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=600"
        ),
        (
            "Invasão da União Soviética",
            "1941-06-22",
            "Hitler quebra o pacto e ataca Stalin na Operação Barbarossa.",
            "A Alemanha rompe o tratado de não agressão e invade a URSS, abrindo a sangrenta Frente Oriental. O avanço alemão é contido pelo rígido inverno russo e pela resistência obstinada dos soviéticos sob o comando de Stalin.",
            "https://images.unsplash.com/photo-1512466699224-9d4157ed2ec9?w=600"
        ),
        (
            "Ataque a Pearl Harbor",
            "1941-12-07",
            "O Japão ataca a base americana, puxando os EUA para o conflito.",
            "Em uma ação surpresa do Império Japonês, a base naval americana no Havaí é bombardeada. O ataque faz os Estados Unidos abandonarem a neutralidade e declararem guerra aos países do Eixo (Alemanha, Itália e Japão).",
            "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=600"
        ),
        (
            "O Brasil na Guerra e as Armas Secretas",
            "1943-08-01",
            "A FEB vai para a Itália enquanto Londres sofre com os foguetes V1 e V2.",
            "O Brasil de Getúlio Vargas declara guerra ao Eixo e prepara a Força Expedicionária Brasileira (FEB) para lutar na Itália. Simultaneamente, a Alemanha desesperada passa a usar 'armas de vingança', atacando Londres com os devastadores mísseis balísticos V1 e V2.",
            "https://images.unsplash.com/photo-1560179707-f14e90ef3623?w=600"
        ),
        (
            "O Dia D",
            "1944-06-06",
            "Desembarque aliado na Normandia para retomar a Europa.",
            "Tropas dos Aliados (norte-americanos, britânicos e canadenses) desembarcam nas praias da Normandia, na França ocupada. Foi a maior operação anfíbia da história, criando uma frente ocidental sólida para marchar em direção à Alemanha.",
            "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=600"
        ),
        (
            "Rendição da Alemanha",
            "1945-05-08",
            "Suicídio de Hitler e o fim da guerra na Europa.",
            "O Exército Vermelho (soviéticos) cerca Berlim. Sem saída, Adolf Hitler comete suicídio no seu bunker no final de abril. No início de maio, o comando militar alemão assina a rendição incondicional.",
            "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=600"
        ),
        (
            "Bombas Atômicas e a Rendição do Japão",
            "1945-08-15",
            "O terror atômico em Hiroshima e Nagasaki encerra o conflito.",
            "Para forçar a rendição japonesa, os EUA lançam a primeira bomba atômica ('Little Boy') sobre Hiroshima no dia 6 de agosto, e a segunda ('Fat Man') sobre Nagasaki no dia 9. Diante da devastação absoluta, o Japão anuncia a rendição, pondo fim oficial à Segunda Guerra Mundial.",
            "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600"
        ),
    ]
    for titulo, data, resumo, definicao, img in acontecimentos_dados:
        cursor.execute(
            f"""INSERT INTO acontecimentos
                    (titulo, data_evento, resumo_timeline, definicao_profunda, imagem_url)
                VALUES ({ph}, {ph}, {ph}, {ph}, {ph});""",
            (titulo, data, resumo, definicao, img)
        )

    # 5. PARTICIPAÇÕES N:M
    # Ev: 1=Marcha Roma, 2=Hitler Chanceler, 3=Guernica, 4=Pacto, 5=Polônia,
    #     6=França, 7=URSS, 8=Pearl Harbor, 9=Brasil/V1V2, 10=Dia D,
    #     11=Rendição Alemanha, 12=Bombas/Japão
    # Per: 1=Mussolini, 2=Hitler, 3=Churchill, 4=De Gaulle,
    #      5=Stalin, 6=Hirohito, 7=Vargas
    print("[INIT] Vinculando Personagens aos Acontecimentos (N:M)...")
    participacoes = [
        # Marcha sobre Roma (1)
        (1,  1, "Comandou os fascistas e exigiu o poder do Estado, instaurando o regime."),
        # Hitler Chanceler (2)
        (2,  2, "Assumiu o controle do Estado, dissolvendo partidos e instaurando o totalitarismo nazista."),
        # Guernica (3)
        (3,  2, "Enviou a força aérea (Luftwaffe) para testar táticas de bombardeio em solo espanhol."),
        (3,  1, "Apoiou os nacionalistas espanhóis junto com a Alemanha, fortalecendo a aliança do Eixo."),
        # Pacto de Não Agressão (4)
        (4,  2, "Assinou o acordo para evitar lutar em duas frentes e garantir a invasão da Polônia."),
        (4,  5, "Fez o pacto buscando ganhar tempo para militarizar a URSS antes de um embate inevitável."),
        # Invasão da Polônia (5)
        (5,  2, "Ordenou a invasão usando a tática da Guerra-Relâmpago (Blitzkrieg)."),
        (5,  3, "Principal crítico de Hitler no Parlamento britânico; sua pressão levou o Reino Unido à guerra."),
        # Queda da França (6)
        (6,  2, "Comemorou a vitória em Paris e determinou a criação da República fantoche de Vichy."),
        (6,  4, "Negou o armistício e viajou a Londres para liderar o movimento da França Livre."),
        # Invasão da URSS (7)
        (7,  2, "Traiu o pacto e ordenou o ataque visando destruir o comunismo e obter petróleo e trigo."),
        (7,  5, "Comandou a resistência soviética mobilizando toda a população contra o invasor alemão."),
        # Pearl Harbor (8)
        (8,  6, "Como imperador, consentiu o ataque estratégico para neutralizar a marinha dos EUA."),
        # Brasil e Armas V1/V2 (9)
        (9,  7, "Cedeu à pressão nacional após ataques a navios e enviou a FEB para lutar contra o Eixo."),
        (9,  3, "Coordenou a defesa civil de Londres e a inteligência britânica contra a chuva de mísseis V1 e V2."),
        # Dia D (10)
        (10, 3, "Articulou com os norte-americanos o planejamento maciço da invasão anfíbia na Normandia."),
        (10, 4, "Apoiou o desembarque organizando a resistência interna francesa para sabotar estradas de ferro."),
        # Rendição da Alemanha (11)
        (11, 2, "Cometeu suicídio no bunker em Berlim para não ser capturado vivo pelos soviéticos."),
        (11, 5, "Suas tropas cercaram Berlim, fincando a bandeira soviética no Reichstag."),
        # Bombas Atômicas / Rendição do Japão (12)
        (12, 6, "Comunicou pelo rádio a rendição incondicional do Japão após o lançamento das bombas em Hiroshima e Nagasaki."),
    ]
    for ev_id, per_id, papel in participacoes:
        cursor.execute(
            f"INSERT INTO participacao (acontecimento_id, personagem_id, papel_historico) VALUES ({ph}, {ph}, {ph});",
            (ev_id, per_id, papel)
        )

    # 6. FINALIZAÇÃO
    conn.commit()
    conn.close()
    print("[INIT] ✅ Banco criado e populado com sucesso!")
    print(f"[INIT] Arquivo: {DATABASE_LOCAL if not USANDO_POSTGRES else 'PostgreSQL (Render)'}")

if __name__ == '__main__':
    inicializar_e_popular()