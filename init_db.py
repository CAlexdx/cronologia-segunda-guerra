# ==============================================================================
# init_db.py — Criação e população do banco de dados
# Execute uma vez com: python init_db.py
# ==============================================================================
import sqlite3
import os

DATABASE = 'banco_local.db'

# Remove o banco anterior para recriar do zero
if os.path.exists(DATABASE):
    os.remove(DATABASE)
    print("[DB] Banco anterior removido.")

conn = sqlite3.connect(DATABASE)
cur = conn.cursor()

# ==============================================================================
# 1. CRIAÇÃO DAS TABELAS
# ==============================================================================
cur.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS acontecimentos (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo           TEXT    NOT NULL,
        data_evento      TEXT    NOT NULL,  -- formato ISO: AAAA-MM-DD
        resumo_timeline  TEXT    NOT NULL,  -- texto curto para o card da timeline
        definicao_profunda TEXT  NOT NULL,  -- texto longo carregado sob demanda
        imagem_url       TEXT              -- URL externa (Wikimedia Commons)
    );

    CREATE TABLE IF NOT EXISTS personagens (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        nome            TEXT    NOT NULL,
        nacionalidade   TEXT    NOT NULL,
        biografia_curta TEXT    NOT NULL
    );

    -- Tabela intermediária N:M com atributo associativo
    CREATE TABLE IF NOT EXISTS participacao (
        acontecimento_id INTEGER NOT NULL REFERENCES acontecimentos(id),
        personagem_id    INTEGER NOT NULL REFERENCES personagens(id),
        papel_historico  TEXT    NOT NULL,
        PRIMARY KEY (acontecimento_id, personagem_id)
    );
""")
print("[DB] Tabelas criadas.")

# ==============================================================================
# 2. INSERÇÃO DOS ACONTECIMENTOS
# ==============================================================================
acontecimentos = [
    (
        "Marcha sobre Roma",
        "1922-10-28",
        "Mussolini e os camisas-negras tomam o poder na Itália, inaugurando a era do fascismo europeu.",
        "Em outubro de 1922, Benito Mussolini mobilizou dezenas de milhares de membros do Partido Nacional Fascista numa marcha intimidadora em direção a Roma. Diante da ameaça, o Rei Vítor Emanuel III recusou-se a decretar estado de sítio e, em vez disso, convidou Mussolini para formar governo. O evento marcou a ascensão do primeiro regime fascista da Europa, servindo de modelo e inspiração direta para Adolf Hitler na Alemanha. A marcha foi um golpe quase sem resistência que demonstrou como instituições democráticas frágeis podiam sucumbir à pressão de movimentos ultranacionalistas violentos.",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Marcia_su_Roma.jpg/1280px-Marcia_su_Roma.jpg"
    ),
    (
        "Hitler se torna Chanceler da Alemanha",
        "1933-01-30",
        "Adolf Hitler é nomeado Chanceler, transformando a República de Weimar numa ditadura em meses.",
        "Em 30 de janeiro de 1933, o presidente Paul von Hindenburg nomeou Adolf Hitler Chanceler da Alemanha, após anos de crescimento eleitoral do Partido Nazista (NSDAP) em meio à crise econômica da Grande Depressão. Hitler rapidamente consolidou o poder: o Incêndio do Reichstag em fevereiro serviu de pretexto para suspender liberdades civis, e o Ato de Habilitação de março conferiu ao governo poderes ditatoriais. A morte de Hindenburg em 1934 permitiu que Hitler unificasse os cargos de presidente e chanceler, tornando-se Führer absoluto. A Alemanha passou de república democrática a Estado totalitário em menos de dois anos.",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Bundesarchiv_Bild_183-S38324%2C_Adolf_Hitler.jpg/800px-Bundesarchiv_Bild_183-S38324%2C_Adolf_Hitler.jpg"
    ),
    (
        "Invasão da Polônia — Início da Guerra",
        "1939-09-01",
        "A Wehrmacht atravessa a fronteira polonesa ao amanhecer, deflagrando a Segunda Guerra Mundial.",
        "Às 4h45 do dia 1º de setembro de 1939, forças alemãs invadiram a Polônia por múltiplas frentes numa tática de guerra relâmpago (Blitzkrieg) que combinava blindados, infantaria motorizada e apoio aéreo massivo da Luftwaffe. Dois dias depois, Reino Unido e França declararam guerra à Alemanha, tornando o conflito uma guerra mundial. A Polônia resistiu por cerca de cinco semanas antes de ser esmagada também pela invasão soviética pelo leste, em 17 de setembro, em cumprimento ao Pacto Molotov-Ribbentrop. A campanha polonesa demonstrou ao mundo a devastadora eficácia da nova doutrina de guerra alemã.",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Bundesarchiv_Bild_183-E10458%2C_Polen%2C_Einmarsch_deutscher_Truppen.jpg/1280px-Bundesarchiv_Bild_183-E10458%2C_Polen%2C_Einmarsch_deutscher_Truppen.jpg"
    ),
    (
        "Queda de Paris",
        "1940-06-14",
        "Tropas alemãs entram em Paris sem resistência. A França capitula em oito semanas de campanha.",
        "Em 10 de maio de 1940, a Alemanha lançou a Caso Amarelo (Fall Gelb), invadindo França, Bélgica e Holanda. O genial flanco pelo maciço de Ardenas cortou as linhas Aliadas, levando ao cerco de Dunquerque, de onde 338.000 soldados foram evacuados entre 26 de maio e 4 de junho. Em 14 de junho, soldados alemães desfilaram pelo Arco do Triunfo numa Paris declarada cidade aberta. Em 22 de junho, a França assinou o armistício num vagão ferroviário em Compiègne — o mesmo local da derrota alemã em 1918, escolhido por Hitler como humilhação simbólica. O norte da França ficou sob ocupação; no sul, o regime colaboracionista de Vichy, liderado pelo Marechal Pétain.",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Bundesarchiv_Bild_101I-126-0350-26A%2C_Paris%2C_Deutsche_Truppen_am_Triumphbogen.jpg/1280px-Bundesarchiv_Bild_101I-126-0350-26A%2C_Paris%2C_Deutsche_Truppen_am_Triumphbogen.jpg"
    ),
    (
        "Batalha da Grã-Bretanha",
        "1940-07-10",
        "A Luftwaffe tenta destruir a RAF numa batalha aérea que decidirá o destino da Europa Ocidental.",
        "De julho a outubro de 1940, a Alemanha travou a maior batalha aérea da história até então, tentando destruir a Royal Air Force (RAF) como prelúdio à invasão anfíbia da Grã-Bretanha (Operação Leão Marinho). Apesar da inferioridade numérica, a RAF, auxiliada pelo radar recém-implantado e pelos caças Spitfire e Hurricane, infligiu perdas insuportáveis à Luftwaffe. Em setembro, Hitler mudou a estratégia para o bombardeio de cidades (o Blitz), aliviando a pressão sobre os aeródromos britânicos. Em outubro, a ameaça de invasão foi suspensa indefinidamente. Foi a primeira grande derrota alemã da guerra, e Churchill a imortalizou: 'Nunca no campo dos conflitos humanos tantos deveram tanto a tão poucos.'",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Battle_of_Britain_Luftwaffe_Heinkel_He_111_croppedH.jpg/1280px-Battle_of_Britain_Luftwaffe_Heinkel_He_111_croppedH.jpg"
    ),
    (
        "Operação Barbarossa",
        "1941-06-22",
        "A maior invasão terrestre da história: 3,8 milhões de soldados do Eixo invadem a União Soviética.",
        "Em 22 de junho de 1941, a Alemanha lançou a Operação Barbarossa, mobilizando 3,8 milhões de soldados, 3.300 tanques e 2.770 aviões ao longo de uma frente de 2.900 km. Três grupos de exércitos avançaram em direção a Leningrado, Moscou e Kiev. Os primeiros meses foram de devastação soviética: o Exército Vermelho perdeu mais de 3 milhões de prisioneiros só em 1941. Contudo, a resistência soviética, a extensão do território, o brutal inverno russo e a logística superextendida alemã interromperam o avanço. A falha em tomar Moscou antes do inverno marcou o início do fim das ambições alemãs a leste. O front oriental tornou-se o maior e mais sangrento teatro de guerra da história, com estimativas de 30 a 40 milhões de mortos.",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Bundesarchiv_Bild_101I-267-0110-31%2C_Russland%2C_Soldaten_mit_Fahrzeug_im_Schlamm.jpg/1280px-Bundesarchiv_Bild_101I-267-0110-31%2C_Russland%2C_Soldaten_mit_Fahrzeug_im_Schlamm.jpg"
    ),
    (
        "Ataque a Pearl Harbor",
        "1941-12-07",
        "Aviões japoneses destroem a frota americana no Havaí. Os EUA entram na guerra no dia seguinte.",
        "Na manhã de 7 de dezembro de 1941, 353 aeronaves japonesas, lançadas de seis porta-aviões, atacaram em duas ondas a base naval americana de Pearl Harbor, no Havaí. Em menos de duas horas, 4 couraçados foram afundados, outros 4 danificados, 188 aeronaves destruídas e 2.403 americanos mortos. O objetivo estratégico era neutralizar a frota do Pacífico para garantir liberdade de ação japonesa no Sudeste Asiático. Porém, os porta-aviões americanos, ausentes naquele dia, sobreviveram — um erro fatal para o Japão. Em 8 de dezembro, o presidente Roosevelt pediu ao Congresso a declaração de guerra, chamando o dia anterior de 'uma data que viverá na infâmia'. Alemanha e Itália declararam guerra aos EUA em 11 de dezembro, unificando os teatros europeu e pacífico num único conflito global.",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Attack_on_Pearl_Harbor_Japanese_planes_view.jpg/1280px-Attack_on_Pearl_Harbor_Japanese_planes_view.jpg"
    ),
    (
        "Batalha de Stalingrado",
        "1942-08-23",
        "O maior e mais sangrento confronto da história humana. A virada decisiva na frente oriental.",
        "De agosto de 1942 a fevereiro de 1943, alemães e soviéticos travaram uma batalha de aniquilação nas ruínas de Stalingrado (atual Volgogrado). O 6º Exército alemão do General Friedrich Paulus avançou até dominar 90% da cidade, mas lutava rua a rua contra soviéticos determinados. Em novembro, a Operação Urano lançou um contra-ataque soviético massivo pelos flancos, cercando 300.000 soldados alemães. Hitler proibiu qualquer retirada. Em 2 de fevereiro de 1943, Paulus — promovido a Marechal-de-Campo na véspera — rendeu-se com 91.000 sobreviventes. A batalha custou mais de 2 milhões de baixas somando os dois lados. Foi o ponto de virada psicológico e estratégico da guerra: a Wehrmacht nunca mais recuperou a iniciativa ofensiva no leste.",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/Bundesarchiv_Bild_183-W0506-316%2C_Russland%2C_Kampf_in_einer_Ortschaft.jpg/1280px-Bundesarchiv_Bild_183-W0506-316%2C_Russland%2C_Kampf_in_einer_Ortschaft.jpg"
    ),
    (
        "Desembarque na Normandia — Dia D",
        "1944-06-06",
        "Maior operação anfíbia da história abre a Frente Ocidental e sela o destino da Alemanha nazista.",
        "Em 6 de junho de 1944, a Operação Overlord lançou 156.000 soldados aliados nas praias da Normandia (codinomes Utah, Omaha, Gold, Juno e Sword) sob comando supremo do General Dwight D. Eisenhower. Paralelamente, 13.000 paraquedistas foram lançados na noite anterior. A praia de Omaha foi o ponto mais sangrento, com quase 2.000 baixas americanas em poucas horas contra posições alemãs em falésias. Apesar das perdas, todos os cinco setores foram tomados. Nos três meses seguintes, 2 milhões de soldados aliados desembarcaram na França. O rompimento em agosto levou à liberação de Paris (25 de agosto) e ao avanço em direção à Alemanha. Com Barbarossa tendo imobilizado e sangrado o exército alemão a leste, o Dia D abriu a morsa que esmagaria o Terceiro Reich.",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Into_the_Jaws_of_Death_23-0455M_edit.jpg/1280px-Into_the_Jaws_of_Death_23-0455M_edit.jpg"
    ),
    (
        "Rendição da Alemanha Nazista",
        "1945-05-08",
        "O Dia da Vitória na Europa (V-E Day): a Alemanha assina a rendição incondicional. O Reich acabou.",
        "Com o Exército Vermelho a poucos quarteirões do Führerbunker, Adolf Hitler suicidou-se em 30 de abril de 1945. Em 7 de maio, na cidade francesa de Reims, o General Alfred Jodl assinou a rendição incondicional alemã perante representantes Aliados; o documento foi reratificado em Berlim na madrugada de 8 de maio a pedido soviético. O Dia 8 de maio tornou-se o V-E Day (Victory in Europe Day), celebrado com euforia nas capitais ocidentais. O Terceiro Reich, que prometera durar mil anos, sobreviveu doze. A guerra na Europa custou estimados 40 a 50 milhões de vidas, incluindo os 6 milhões de judeus assassinados no Holocausto. A Alemanha seria dividida em zonas de ocupação, semente da Guerra Fria.",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Jodi_signs_German_Instrument_of_Surrender_-_Reims_-_1945.jpg/1280px-Jodi_signs_German_Instrument_of_Surrender_-_Reims_-_1945.jpg"
    ),
    (
        "Bomba Atômica em Hiroshima",
        "1945-08-06",
        "O Enola Gay lança 'Little Boy' sobre Hiroshima. A era nuclear chega com 80.000 mortos instantâneos.",
        "Às 8h15 do dia 6 de agosto de 1945, o bombardeiro B-29 Enola Gay, pilotado pelo Coronel Paul Tibbets, lançou sobre Hiroshima a bomba atômica 'Little Boy' — um dispositivo de urânio com potência equivalente a 15 kilotones de TNT. A detonação a 600 metros de altitude destruiu imediatamente 13 km² da cidade. Entre 70.000 e 80.000 pessoas morreram instantaneamente; o total até o final de 1945, incluindo mortes por radiação, chegou a 140.000. Três dias depois, em 9 de agosto, uma segunda bomba ('Fat Man', de plutônio) foi lançada sobre Nagasaki, matando entre 40.000 e 80.000 pessoas. As duas bombas foram o produto do Projeto Manhattan, esforço científico secreto que envolveu mais de 130.000 pessoas e custou 2 bilhões de dólares (equivalente a 28 bilhões atuais).",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Atomic_bombing_of_Japan.jpg/1280px-Atomic_bombing_of_Japan.jpg"
    ),
    (
        "Rendição Oficial do Japão",
        "1945-09-02",
        "A bordo do USS Missouri, o Japão assina a rendição incondicional. A Segunda Guerra Mundial termina.",
        "Em 15 de agosto de 1945, o Imperador Hirohito transmitiu pelo rádio o Rescript Imperial de Rendição — a primeira vez que os japoneses ouviam a voz do Imperador — anunciando a aceitação dos termos da Declaração de Potsdam. A cerimônia formal de rendição ocorreu em 2 de setembro de 1945, no convés do couraçado USS Missouri, ancorado na Baía de Tóquio. O Ministro das Relações Exteriores Mamoru Shigemitsu assinou pelo governo japonês; o General Yoshijiro Umezu, pelas Forças Armadas. O General Douglas MacArthur presidiu a cerimônia em nome das potências Aliadas, declarando: 'É meu fervente desejo, e o desejo de toda a humanidade, que da tragédia passada brote um mundo melhor.' O documento foi então assinado por representantes dos EUA, China, Reino Unido, URSS, Austrália, Canadá, França, Holanda e Nova Zelândia. A Segunda Guerra Mundial estava formalmente encerrada após seis anos, um mês e um dia.",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Japan_signs_surrender.jpg/1280px-Japan_signs_surrender.jpg"
    ),
]

cur.executemany("""
    INSERT INTO acontecimentos (titulo, data_evento, resumo_timeline, definicao_profunda, imagem_url)
    VALUES (?, ?, ?, ?, ?)
""", acontecimentos)
print(f"[DB] {len(acontecimentos)} acontecimentos inseridos.")

# ==============================================================================
# 3. INSERÇÃO DOS PERSONAGENS
# ==============================================================================
personagens = [
    ("Benito Mussolini",    "Italiana",    "Fundador do fascismo e Duce da Itália. Aliado de Hitler até o fim, foi executado por partisans em abril de 1945."),
    ("Adolf Hitler",        "Alemã",       "Führer do Terceiro Reich. Responsável pelo desencadeamento da guerra e pelo Holocausto. Suicidou-se em abril de 1945."),
    ("Winston Churchill",   "Britânica",   "Primeiro-Ministro britânico durante a maior parte da guerra. Símbolo da resistência ao nazismo com seus discursos históricos."),
    ("Franklin D. Roosevelt","Americana",  "Presidente dos EUA que conduziu o país da neutralidade à liderança Aliada. Morreu em abril de 1945, antes do fim da guerra."),
    ("Josef Stalin",        "Soviética",   "Líder da URSS. Conduziu o país pela maior carnificina da guerra e emergiu como uma das potências dominantes do pós-guerra."),
    ("Erwin Rommel",        "Alemã",       "O 'Raposa do Deserto'. Comandou o Afrika Korps no Norte da África e as defesas costeiras na Normandia. Forçado ao suicídio em 1944."),
    ("Dwight D. Eisenhower","Americana",   "Comandante Supremo das forças aliadas na Europa. Planejou e executou o Dia D. Tornou-se presidente dos EUA em 1953."),
    ("Douglas MacArthur",   "Americana",   "Comandante das forças aliadas no Pacífico. Presidiu a rendição formal do Japão a bordo do USS Missouri em 2 de setembro de 1945."),
    ("Hirohito",            "Japonesa",    "Imperador do Japão durante toda a guerra. Seu discurso de rádio em 15 de agosto de 1945 anunciou a rendição japonesa ao povo."),
    ("Isoroku Yamamoto",    "Japonesa",    "Arquiteto do ataque a Pearl Harbor e comandante da Frota Combinada japonesa. Morto em emboscada aérea em 1943."),
    ("Friedrich Paulus",    "Alemã",       "Comandante do 6º Exército alemão em Stalingrado. Promovido a Marechal-de-Campo horas antes de se render aos soviéticos."),
    ("Georgy Zhukov",       "Soviética",   "O maior general soviético da guerra. Defendeu Moscou, planejou a contra-ofensiva de Stalingrado e liderou o assalto final a Berlim."),
    ("Paul Tibbets",        "Americana",   "Piloto do Enola Gay. Lançou a primeira bomba atômica sobre Hiroshima em 6 de agosto de 1945, mudando a história da humanidade."),
    ("Mamoru Shigemitsu",   "Japonesa",    "Ministro das Relações Exteriores do Japão. Assinou os documentos de rendição a bordo do USS Missouri em nome do governo japonês."),
    ("Charles de Gaulle",   "Francesa",    "Líder da França Livre. Recusou-se a aceitar a derrota de 1940 e organizou a resistência francesa a partir de Londres."),
]

cur.executemany("""
    INSERT INTO personagens (nome, nacionalidade, biografia_curta)
    VALUES (?, ?, ?)
""", personagens)
print(f"[DB] {len(personagens)} personagens inseridos.")

# ==============================================================================
# 4. INSERÇÃO DAS PARTICIPAÇÕES (TABELA N:M)
# IDs dos acontecimentos: 1=Marcha Roma, 2=Hitler Chanceler, 3=Invasão Polônia,
#   4=Queda Paris, 5=Batalha Grã-Bretanha, 6=Barbarossa, 7=Pearl Harbor,
#   8=Stalingrado, 9=Dia D, 10=Rendição Alemanha, 11=Hiroshima, 12=Rendição Japão
# IDs dos personagens: 1=Mussolini, 2=Hitler, 3=Churchill, 4=Roosevelt, 5=Stalin,
#   6=Rommel, 7=Eisenhower, 8=MacArthur, 9=Hirohito, 10=Yamamoto, 11=Paulus,
#   12=Zhukov, 13=Tibbets, 14=Shigemitsu, 15=De Gaulle
# ==============================================================================
participacoes = [
    # Marcha sobre Roma (1)
    (1,  1,  "Líder e organizador da Marcha. Intimidou o Rei Vítor Emanuel III a nomeá-lo Primeiro-Ministro."),
    # Hitler Chanceler (2)
    (2,  2,  "Nomeado Chanceler em 30 de janeiro de 1933. Rapidamente transformou a república em ditadura."),
    # Invasão da Polônia (3)
    (3,  2,  "Ordenou a invasão em 1º de setembro de 1939, desencadeando a guerra."),
    (3,  3,  "Declarou guerra à Alemanha em 3 de setembro de 1939 em nome do Reino Unido."),
    (3,  4,  "Monitorou os eventos, ainda navegando entre neutralidade e apoio aos Aliados."),
    # Queda de Paris (4)
    (4,  2,  "Ordenou a campanha no oeste e escolheu pessoalmente Compiègne para a assinatura do armistício como humilhação simbólica."),
    (4,  6,  "Comandou a 7ª Divisão Panzer na frente francesa com agressividade notável."),
    (4,  15, "Recusou a rendição e transmitiu pelo rádio da BBC sua famosa Chamada de 18 de junho, fundando a França Livre."),
    # Batalha da Grã-Bretanha (5)
    (5,  2,  "Autorizou a mudança estratégica para o Blitz sobre cidades civis, aliviando inadvertidamente a pressão sobre a RAF."),
    (5,  3,  "Liderou a resistência britânica com discursos históricos como 'Nunca nos renderemos'. Gerenciou a defesa aérea."),
    # Operação Barbarossa (6)
    (6,  2,  "Planejou e ordenou a invasão da URSS em 22 de junho de 1941, abrindo a frente que destruiria o Terceiro Reich."),
    (6,  5,  "Comandou a resistência soviética. Inicialmente apanhado de surpresa, reorganizou o Exército Vermelho."),
    (6,  12, "Defendeu Moscou em dezembro de 1941, infligindo a primeira derrota terrestre significativa à Wehrmacht."),
    # Pearl Harbor (7)
    (7,  9,  "Imperador durante o ataque; o papel exato de sua aprovação prévia ainda é debatido por historiadores."),
    (7,  10, "Planejou e autorizou o ataque a Pearl Harbor como estratégia para neutralizar a frota americana do Pacífico."),
    (7,  4,  "Discursou ao Congresso no dia seguinte pedindo declaração de guerra, chamando 7 de dezembro de 'data que viverá na infâmia'."),
    # Batalha de Stalingrado (8)
    (8,  2,  "Proibiu qualquer retirada alemã mesmo quando o cerco soviético tornou a situação desesperadora."),
    (8,  5,  "Autorizou a Operação Urano, o contra-ataque que cercou o 6º Exército alemão."),
    (8,  11, "Comandou o 6º Exército em Stalingrado. Rendeu-se em 2 de fevereiro de 1943 com 91.000 sobreviventes."),
    (8,  12, "Planejou e executou a Operação Urano, o cerco que destruiu o 6º Exército e virou a guerra."),
    # Dia D — Normandia (9)
    (9,  7,  "Comandante Supremo da Operação Overlord. Tomou a decisão final de lançar o desembarque na janela climática de 6 de junho."),
    (9,  6,  "Comandava as defesas alemãs na Normandia. Acreditava que a batalha seria vencida ou perdida nas primeiras 24 horas."),
    (9,  3,  "Coordenou politicamente a aliança e manteve Churchill informado das decisões estratégicas com Roosevelt."),
    (9,  4,  "Aprovou e financiou a Operação Overlord. Acompanhou os desdobramentos de Washington."),
    # Rendição da Alemanha (10)
    (10, 2,  "Suicidou-se em 30 de abril de 1945 no Führerbunker, dois dias antes da queda de Berlim."),
    (10, 3,  "Celebrou a vitória em Londres diante de multidões. 'Este é o seu dia', disse ao povo britânico."),
    (10, 5,  "O Exército Vermelho tomou Berlim. Stalin presidiu a reratificação da rendição em 8 de maio."),
    (10, 12, "Comandou o assalto final a Berlim pelo Exército Vermelho, completando a vitória soviética na Europa."),
    # Hiroshima (11)
    (11, 4,  "Autorizou o uso das bombas atômicas. Morreu antes do lançamento; a decisão foi mantida por Truman."),
    (11, 9,  "Imperador durante o bombardeio. O ataque acelerou sua decisão de aceitar a rendição incondicional."),
    (11, 13, "Pilotou o Enola Gay e lançou 'Little Boy' sobre Hiroshima às 8h15 de 6 de agosto de 1945."),
    # Rendição do Japão (12)
    (12, 9,  "Transmitiu pelo rádio o anúncio da rendição em 15 de agosto. Assinou o Rescrito Imperial de Rendição."),
    (12, 8,  "Presidiu a cerimônia de rendição a bordo do USS Missouri. Tornou-se o administrador da ocupação americana do Japão."),
    (12, 14, "Assinou os documentos de rendição em nome do governo japonês a bordo do USS Missouri em 2 de setembro de 1945."),
]

cur.executemany("""
    INSERT INTO participacao (acontecimento_id, personagem_id, papel_historico)
    VALUES (?, ?, ?)
""", participacoes)
print(f"[DB] {len(participacoes)} participações N:M inseridas.")

conn.commit()
conn.close()
print("\n[DB] ✅ Banco de dados criado e populado com sucesso!")
print(f"[DB] Arquivo: {DATABASE}")