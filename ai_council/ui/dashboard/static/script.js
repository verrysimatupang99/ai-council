document.addEventListener('DOMContentLoaded', () => {
    const sessionList = document.getElementById('session-list');
    const activeSessionInfo = document.getElementById('active-session-info');
    const responsesContainer = document.getElementById('responses-container');
    const synthesisPanel = document.getElementById('synthesis-panel');
    const synthesisContent = document.getElementById('synthesis-content');

    // Fetch and display sessions
    async function loadSessions() {
        try {
            const response = await fetch('/api/sessions');
            const sessions = await response.json();
            
            sessionList.innerHTML = '';
            
            if (sessions.length === 0) {
                sessionList.innerHTML = '<div class="no-data">No sessions found.</div>';
                return;
            }

            sessions.forEach(session => {
                const item = document.createElement('div');
                item.className = 'session-item';
                item.innerHTML = `
                    <h4>${session.query}</h4>
                    <div class="meta">${new Date(session.timestamp).toLocaleString()} | Rounds: ${session.rounds}</div>
                `;
                item.onclick = () => loadSessionDetails(session.id, item);
                sessionList.appendChild(item);
            });
        } catch (error) {
            console.error('Error loading sessions:', error);
            sessionList.innerHTML = '<div class="error">Failed to load history.</div>';
        }
    }

    // Fetch and display full details
    async function loadSessionDetails(id, element) {
        // Update UI state
        document.querySelectorAll('.session-item').forEach(el => el.classList.remove('active'));
        element.classList.add('active');
        
        responsesContainer.innerHTML = '<div class="loading">Loading details...</div>';
        synthesisPanel.classList.add('hidden');

        try {
            const response = await fetch(`/api/sessions/${id}`);
            const session = await response.json();
            
            // Header
            activeSessionInfo.innerHTML = `
                <h2>${session.query}</h2>
                <p class="meta">ID: ${session.id} | ${new Date(session.timestamp).toLocaleString()} | Total Cost: $${session.total_cost.toFixed(4)}</p>
            `;

            // Synthesis
            if (session.final_synthesis) {
                synthesisContent.innerHTML = marked.parse(session.final_synthesis);
                synthesisPanel.classList.remove('hidden');
            }

            // Responses
            responsesContainer.innerHTML = '';
            session.responses.forEach(resp => {
                const card = document.createElement('div');
                const agentClass = `agent-${resp.agent_name.toLowerCase()}`;
                card.className = `response-card ${agentClass}`;
                
                card.innerHTML = `
                    <div class="response-header">
                        <span class="agent-name">${resp.agent_name}</span>
                        <span class="response-meta">Round ${resp.round} | ${resp.model} | ${resp.latency_ms.toFixed(0)}ms</span>
                    </div>
                    <div class="response-body">${resp.content}</div>
                `;
                responsesContainer.appendChild(card);
            });

        } catch (error) {
            console.error('Error loading session details:', error);
            responsesContainer.innerHTML = '<div class="error">Failed to load session details.</div>';
        }
    }

    loadSessions();
});
