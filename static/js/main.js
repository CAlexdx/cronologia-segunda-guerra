// ==============================================================================
// static/js/main.js — Gerenciamento Assíncrono da Linha do Tempo (Lazy Loading)
// ==============================================================================

document.addEventListener("DOMContentLoaded", () => {
    // Seleção de elementos da estrutura
    const timelineTrack  = document.getElementById("timeline-track");
    const loadingState   = document.getElementById("loading-state");
    const errorState     = document.getElementById("error-state");

    // Elementos do Modal
    const modalOverlay   = document.getElementById("modal-overlay");
    const modalContent   = document.getElementById("modal-content");
    const modalLoading   = document.getElementById("modal-loading");
    const modalClose     = document.getElementById("modal-close");

    // Campos Internos do Modal
    const modalImagem    = document.getElementById("modal-imagem");
    const modalData      = document.getElementById("modal-data");
    const modalTitulo    = document.getElementById("modal-titulo");
    const modalDefinicao = document.getElementById("modal-definicao");

    // FIX: nome corrigido de "personajesGrid" (bug ortográfico) para "personagensGrid"
    // A variável estava sendo declarada com 'j' (espanhol) mas usada com 'g' (português)
    // dentro de abrirDetalhesEvento, causando ReferenceError silencioso.
    const personagensGrid = document.getElementById("personagens-grid");

    // ==========================================================================
    // 1. CARREGAMENTO DA TIMELINE LEVE (ROTA 1)
    // ==========================================================================

    // FIX: função declarada antes de ser exposta no window,
    // garantindo que a referência global esteja disponível imediatamente,
    // inclusive para o botão "Tentar novamente" do HTML.
    function carregarTimeline() {
        loadingState.classList.remove("hidden");
        errorState.classList.add("hidden");
        timelineTrack.innerHTML = "";

        fetch("/api/eventos")
            .then(response => {
                if (!response.ok) throw new Error("Resposta inválida do servidor");
                return response.json();
            })
            .then(eventos => {
                loadingState.classList.add("hidden");

                if (eventos.length === 0) {
                    timelineTrack.innerHTML = "<p style='text-align:center; color:var(--text-secondary); width: 100vw;'>Nenhum evento populado no banco.</p>";
                    return;
                }

                // Monta os blocos de forma alternada (left = cima, right = baixo no CSS horizontal)
                eventos.forEach((evento, index) => {
                    const lado  = index % 2 === 0 ? "left" : "right";
                    const bloco = criarBlocoTimeline(evento, lado);
                    timelineTrack.appendChild(bloco);
                });
            })
            .catch(error => {
                console.error("[ERRO SCRIPT]:", error);
                loadingState.classList.add("hidden");
                errorState.classList.remove("hidden");
            });
    }

    // Vincula a função globalmente ANTES da inicialização,
    // garantindo que o botão "Tentar novamente" do HTML sempre a encontre.
    window.carregarTimeline = carregarTimeline;

    // Construtor do bloco HTML para cada evento
    function criarBlocoTimeline(evento, lado) {
        const block = document.createElement("div");
        block.className = `timeline-block ${lado}`;

        const dataBr = formatarData(evento.data_evento);

        block.innerHTML = `
            <div class="timeline-node"></div>
            <div class="timeline-card" data-id="${evento.id}">
                <p class="card-data">${dataBr}</p>
                <h3 class="card-titulo">${evento.titulo}</h3>
                <p class="card-resumo">${evento.resumo_timeline}</p>
            </div>
        `;

        // Ouvinte de clique para carregar os detalhes sob demanda (Lazy Loading)
        const card = block.querySelector(".timeline-card");
        card.addEventListener("click", () => {
            abrirDetalhesEvento(evento.id);
        });

        return block;
    }

    // ==========================================================================
    // 2. DETALHES SOB DEMANDA E INTERAÇÃO N:M (ROTA 2)
    // ==========================================================================
    function abrirDetalhesEvento(id) {
        modalOverlay.classList.add("active");
        modalLoading.classList.remove("hidden");
        modalContent.classList.add("hidden");

        fetch(`/api/evento/${id}`)
            .then(response => {
                if (!response.ok) throw new Error("Erro ao carregar dados do evento.");
                return response.json();
            })
            .then(data => {
                modalData.innerText      = formatarData(data.data_evento);
                modalTitulo.innerText    = data.titulo;
                modalDefinicao.innerText = data.definicao_profunda;

                if (data.imagem_url) {
                    modalImagem.src                    = data.imagem_url;
                    modalImagem.alt                    = data.titulo;
                    modalImagem.parentElement.style.display = "block";
                } else {
                    modalImagem.parentElement.style.display = "none";
                }

                // Renderiza as Figuras Históricas (Relacionamento Muitos-para-Muitos)
                // FIX: usa a variável corretamente nomeada "personagensGrid"
                personagensGrid.innerHTML = "";
                if (data.personagens && data.personagens.length > 0) {
                    data.personagens.forEach(p => {
                        const pCard = document.createElement("div");
                        pCard.className = "personagem-card";
                        pCard.innerHTML = `
                            <h4 class="personagem-nome">${p.nome}</h4>
                            <span class="personagem-nacionalidade">${p.nacionalidade}</span>
                            <p class="personagem-papel"><strong>Atuação:</strong> ${p.papel_historico}</p>
                        `;
                        personagensGrid.appendChild(pCard);
                    });
                } else {
                    personagensGrid.innerHTML = "<p style='grid-column: 1/-1; color: var(--text-muted); text-align: center; padding: 20px;'>Nenhuma figura mapeada para este marco.</p>";
                }

                modalLoading.classList.add("hidden");
                modalContent.classList.remove("hidden");
            })
            .catch(error => {
                console.error("[ERRO MODAL]:", error);
                modalData.innerText      = "Erro";
                modalTitulo.innerText    = "Falha na requisição";
                modalDefinicao.innerText = "Não foi possível buscar as informações detalhadas no servidor.";
                modalLoading.classList.add("hidden");
                modalContent.classList.remove("hidden");
            });
    }

    // ==========================================================================
    // 3. FUNÇÕES AUXILIARES (FECHAMENTO E DATA)
    // ==========================================================================
    function formatarData(dataString) {
        if (!dataString) return "";
        const partes = dataString.split("-");
        if (partes.length !== 3) return dataString;
        return `${partes[2]}/${partes[1]}/${partes[0]}`;
    }

    modalClose.addEventListener("click", () => {
        modalOverlay.classList.remove("active");
    });

    modalOverlay.addEventListener("click", (e) => {
        if (e.target === modalOverlay) {
            modalOverlay.classList.remove("active");
        }
    });

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && modalOverlay.classList.contains("active")) {
            modalOverlay.classList.remove("active");
        }
    });

    // Inicializa a chamada assim que a página abre
    carregarTimeline();
});