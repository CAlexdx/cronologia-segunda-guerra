// ==============================================================================
// static/js/main.js — Gerenciamento Assíncrono da Linha do Tempo (Lazy Loading)
// ==============================================================================

document.addEventListener("DOMContentLoaded", () => {

    // Elementos da estrutura
    const timelineTrack  = document.getElementById("timeline-track");
    const loadingState   = document.getElementById("loading-state");
    const errorState     = document.getElementById("error-state");

    // Elementos do Modal
    const modalOverlay   = document.getElementById("modal-overlay");
    const modalContent   = document.getElementById("modal-content");
    const modalLoading   = document.getElementById("modal-loading");
    const modalClose     = document.getElementById("modal-close");

    // Campos internos do Modal
    const modalImagem    = document.getElementById("modal-imagem");
    const modalData      = document.getElementById("modal-data");
    const modalTitulo    = document.getElementById("modal-titulo");
    const modalDefinicao = document.getElementById("modal-definicao");

    // FIX (mantido): variável declarada com nome correto em português.
    // A versão anterior tinha "personajesGrid" (espanhol), causando ReferenceError.
    const personagensGrid = document.getElementById("personagens-grid");

    // ==========================================================================
    // 1. CARREGAMENTO DA TIMELINE LEVE (ROTA 1)
    // ==========================================================================

    // FIX (mantido): função declarada antes de window.carregarTimeline,
    // garantindo que a referência global exista quando o botão "Tentar novamente"
    // do HTML for clicado (mesmo antes do DOMContentLoaded terminar).
    function carregarTimeline() {
        loadingState.classList.remove("hidden");
        errorState.classList.add("hidden");
        timelineTrack.innerHTML = "";

        fetch("/api/eventos")
            .then(res => {
                if (!res.ok) throw new Error("Resposta inválida do servidor");
                return res.json();
            })
            .then(eventos => {
                loadingState.classList.add("hidden");

                if (eventos.length === 0) {
                    timelineTrack.innerHTML = "<p style='color:var(--text-secondary);padding:40px;'>Nenhum evento populado no banco.</p>";
                    return;
                }

                eventos.forEach((evento, index) => {
                    const lado  = index % 2 === 0 ? "left" : "right";
                    timelineTrack.appendChild(criarBlocoTimeline(evento, lado));
                });
            })
            .catch(err => {
                console.error("[ERRO SCRIPT]:", err);
                loadingState.classList.add("hidden");
                errorState.classList.remove("hidden");
            });
    }

    // Expõe globalmente para o botão "Tentar novamente" do HTML
    window.carregarTimeline = carregarTimeline;

    // Constrói o bloco HTML de cada marco da timeline
    function criarBlocoTimeline(evento, lado) {
        const block  = document.createElement("div");
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

        block.querySelector(".timeline-card").addEventListener("click", () => {
            abrirDetalhesEvento(evento.id);
        });

        return block;
    }

    // ==========================================================================
    // 2. DETALHES SOB DEMANDA — ROTA 2 (Lazy Loading + N:M)
    // ==========================================================================
    function abrirDetalhesEvento(id) {
        modalOverlay.classList.add("active");
        modalLoading.classList.remove("hidden");
        modalContent.classList.add("hidden");

        fetch(`/api/evento/${id}`)
            .then(res => {
                if (!res.ok) throw new Error("Erro ao carregar dados do evento.");
                return res.json();
            })
            .then(data => {
                modalData.innerText      = formatarData(data.data_evento);
                modalTitulo.innerText    = data.titulo;

                // CONTRATO: app.py retorna 'definicao_profunda' (mesmo nome da coluna).
                // init_db.py cria a coluna com este nome para fechar o ciclo.
                modalDefinicao.innerText = data.definicao_profunda;

                if (data.imagem_url) {
                    modalImagem.src = data.imagem_url;
                    modalImagem.alt = data.titulo;
                    modalImagem.parentElement.style.display = "block";
                } else {
                    modalImagem.parentElement.style.display = "none";
                }

                // Renderiza as figuras históricas — relacionamento N:M
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
                    personagensGrid.innerHTML = "<p style='grid-column:1/-1;color:var(--text-muted);text-align:center;padding:20px;'>Nenhuma figura mapeada para este marco.</p>";
                }

                modalLoading.classList.add("hidden");
                modalContent.classList.remove("hidden");
            })
            .catch(err => {
                console.error("[ERRO MODAL]:", err);
                modalData.innerText      = "Erro";
                modalTitulo.innerText    = "Falha na requisição";
                modalDefinicao.innerText = "Não foi possível buscar as informações detalhadas no servidor.";
                modalLoading.classList.add("hidden");
                modalContent.classList.remove("hidden");
            });
    }

    // ==========================================================================
    // 3. AUXILIARES — DATA E FECHAMENTO DO MODAL
    // ==========================================================================
    function formatarData(dataString) {
        if (!dataString) return "";
        const partes = dataString.split("-");
        if (partes.length !== 3) return dataString;
        return `${partes[2]}/${partes[1]}/${partes[0]}`;
    }

    // Fechar pelo botão X
    modalClose.addEventListener("click", () => {
        modalOverlay.classList.remove("active");
    });

    // Fechar clicando fora do painel
    modalOverlay.addEventListener("click", e => {
        if (e.target === modalOverlay) modalOverlay.classList.remove("active");
    });

    // Fechar com tecla Esc
    document.addEventListener("keydown", e => {
        if (e.key === "Escape" && modalOverlay.classList.contains("active")) {
            modalOverlay.classList.remove("active");
        }
    });

    // Inicialização
    carregarTimeline();
});