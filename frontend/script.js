const API_URL = "http://localhost:8081/api/analyze";

async function analyzeSite() {
    const urlInput = document.getElementById('urlInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const btnText = document.getElementById('btnText');
    const loader = document.getElementById('loader');
    const resultsSection = document.getElementById('resultsSection');
    const issuesList = document.getElementById('issuesList');

    let url = urlInput.value.trim();
    if (!url) {
        alert("Por favor, insira um URL válido.");
        return;
    }

    if (!url.startsWith('http://') && !url.startsWith('https://')) {
        url = 'https://' + url;
    }

    // Reset UI
    resultsSection.classList.add('hidden');
    issuesList.innerHTML = '';

    // Loading State
    analyzeBtn.disabled = true;
    btnText.textContent = "A analisar...";
    loader.classList.remove('hidden');

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Falha na análise (Status: ${response.status}). Detalhes: ${errorText}`);
        }

        const data = await response.json();
        displayResults(data);

    } catch (error) {
        alert("Erro ao analisar o site: " + error.message);
    } finally {
        analyzeBtn.disabled = false;
        btnText.textContent = "Verificar Conformidade";
        loader.classList.add('hidden');
    }
}

function displayResults(data) {
    const resultsSection = document.getElementById('resultsSection');
    const scoreValue = document.getElementById('scoreValue');
    const statusText = document.getElementById('statusText');
    const pagesScanned = document.getElementById('pagesScanned');
    const issuesList = document.getElementById('issuesList');

    // Show section
    resultsSection.classList.remove('hidden');

    // Update Score
    scoreValue.textContent = data.score;
    // Animate score color based on value
    const circle = document.querySelector('.score-circle');
    if (data.score >= 90) circle.style.borderColor = "var(--success)";
    else if (data.score >= 60) circle.style.borderColor = "var(--warning)";
    else circle.style.borderColor = "var(--danger)";

    statusText.textContent = data.status;
    pagesScanned.textContent = `Páginas analisadas: ${data.scanned_pages}`;

    // Update Issues
    if (data.issues.length === 0) {
        issuesList.innerHTML = `<div class="issue-item low"><div class="issue-header"><span class="issue-title">Sem inconformidades detetadas</span></div><p>Parabéns! O site parece cumprir as normas verificadas.</p></div>`;
    } else {
        data.issues.forEach(issue => {
            const div = document.createElement('div');
            // Assuming localhost:8081 for images - dynamic in prod
            const imageUrl = `http://localhost:8081/${issue.screenshot}`;

            div.className = `issue-item ${issue.severity}`;

            const isSuccess = issue.severity === 'success';
            const icon = isSuccess ? '<i class="fa-solid fa-check-circle"></i>' : '<i class="fa-solid fa-triangle-exclamation"></i>';
            const badgeClass = isSuccess ? 'issue-badge success' : 'issue-badge';
            const suggestionTitle = isSuccess ? 'Estado:' : 'Como Corrigir:';
            const suggestionIcon = isSuccess ? '<i class="fa-solid fa-thumbs-up"></i>' : '<i class="fa-solid fa-lightbulb"></i>';

            div.innerHTML = `
                <div class="issue-header">
                    <span class="issue-title">${icon} ${issue.rule}</span>
                    <span class="${badgeClass}">${issue.severity.toUpperCase()}</span>
                </div>
                
                <div class="issue-content">
                    <div class="issue-details">
                        <p class="description"><strong>${isSuccess ? 'Info' : 'Erro'}:</strong> ${issue.description}</p>
                        
                        ${issue.context ? `
                        <div class="context-box">
                            <strong>${isSuccess ? 'Contexto Verificado' : 'Contexto Encontrado'}:</strong>
                            <blockquote>"${issue.context}"</blockquote>
                        </div>` : ''}

                        ${issue.location_guide ? `
                        <div class="location-box" style="margin-top: 10px; padding: 10px; background: #eef2f5; border-left: 4px solid #2c3e50; border-radius: 4px;">
                            <i class="fa-solid fa-code-branch"></i>
                            <strong>Guia de Localização (Técnico):</strong>
                            <code style="display: block; margin-top: 5px; color: ${isSuccess ? 'green' : '#d63384'};">${issue.location_guide}</code>
                        </div>` : ''}
                        
                        <div class="suggestion-box" style="${isSuccess ? 'background-color: #d1e7dd; border-color: #badbcc;' : ''}">
                            ${suggestionIcon}
                            <strong>${suggestionTitle}</strong>
                            <p>${issue.suggestion}</p>
                        </div>

                        <a href="${issue.url}" target="_blank" class="link-btn">
                            <i class="fa-solid fa-external-link-alt"></i> Ver na Página
                        </a>
                    </div>
                    
                    <div class="issue-image">
                        <img src="${imageUrl}" alt="Screenshot da falha" onclick="window.open('${imageUrl}', '_blank')">
                        <small>Clique para ampliar</small>
                    </div>
                </div>
            `;
            issuesList.appendChild(div);
        });
    }

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}
