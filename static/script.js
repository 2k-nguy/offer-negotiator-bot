// JavaScript for Neogiator Bot Web Interface
let currentContextId = null;
let strategies = [];

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    loadStrategies();
    setupEventListeners();
}

function loadStrategies() {
    fetch('/api/strategies')
        .then(response => response.json())
        .then(data => {
            strategies = data;
            populateStrategySelect();
        })
        .catch(error => {
            console.error('Error loading strategies:', error);
            showAlert('Error loading strategies', 'danger');
        });
}

function populateStrategySelect() {
    const select = document.getElementById('strategySelect');
    select.innerHTML = '';
    
    strategies.forEach(strategy => {
        const option = document.createElement('option');
        option.value = strategy.value;
        option.textContent = strategy.name;
        select.appendChild(option);
    });
}

function setupEventListeners() {
    // Setup form submission
    document.getElementById('setupForm').addEventListener('submit', handleSetup);
    
    // Message sending
    document.getElementById('sendMessage').addEventListener('click', sendMessage);
    document.getElementById('messageInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Strategy update
    document.getElementById('updateStrategy').addEventListener('click', updateStrategy);
}

function handleSetup(e) {
    e.preventDefault();
    
    const formData = {
        company_name: document.getElementById('companyName').value,
        position: document.getElementById('position').value,
        user_profile: {
            years_experience: parseInt(document.getElementById('yearsExperience').value),
            industry: document.getElementById('industry').value,
            education_level: document.getElementById('educationLevel').value,
            key_achievement: document.getElementById('keyAchievement').value,
            primary_skill: document.getElementById('primarySkill').value,
            certifications: [],
            leadership_experience: true,
            industry_awards: []
        },
        target_salary: parseInt(document.getElementById('targetSalary').value) || null,
        target_benefits: document.getElementById('targetBenefits').value.split(',').map(s => s.trim()).filter(s => s),
        deal_breakers: document.getElementById('dealBreakers').value.split(',').map(s => s.trim()).filter(s => s)
    };
    
    showLoading();
    
    fetch('/api/create_context', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            currentContextId = data.context_id;
            showNegotiationSection();
            loadNegotiationStatus();
            showAlert('Negotiation context created successfully!', 'success');
        } else {
            showAlert(data.error || 'Failed to create context', 'danger');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error:', error);
        showAlert('Error creating negotiation context', 'danger');
    });
}

function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    
    if (!message || !currentContextId) {
        return;
    }
    
    // Add company message to chat
    addMessageToChat('company', 'Company', message);
    messageInput.value = '';
    
    showLoading();
    
    fetch('/api/generate_response', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            context_id: currentContextId,
            message: message
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            addMessageToChat('bot', 'Neogiator Bot', data.response);
            loadNegotiationStatus(); // Refresh status
        } else {
            showAlert(data.error || 'Failed to generate response', 'danger');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error:', error);
        showAlert('Error generating response', 'danger');
    });
}

function addMessageToChat(sender, senderName, content) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender} new`;
    
    const timestamp = new Date().toLocaleTimeString();
    
    messageDiv.innerHTML = `
        <div class="message-header">${senderName}</div>
        <div class="message-content">${content}</div>
        <div class="message-time">${timestamp}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Remove animation class after animation completes
    setTimeout(() => {
        messageDiv.classList.remove('new');
    }, 300);
}

function loadNegotiationStatus() {
    if (!currentContextId) return;
    
    fetch(`/api/negotiation_status?context_id=${currentContextId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showAlert(data.error, 'danger');
                return;
            }
            
            displayNegotiationStatus(data);
        })
        .catch(error => {
            console.error('Error loading status:', error);
        });
}

function displayNegotiationStatus(status) {
    const statusDiv = document.getElementById('negotiationStatus');
    
    const strategyClass = `strategy-${status.strategy.replace('_', '-')}`;
    const strategyName = status.strategy.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    
    statusDiv.innerHTML = `
        <div class="status-item">
            <span class="status-label">Company:</span>
            <span class="status-value">${status.company}</span>
        </div>
        <div class="status-item">
            <span class="status-label">Position:</span>
            <span class="status-value">${status.position}</span>
        </div>
        <div class="status-item">
            <span class="status-label">Strategy:</span>
            <span class="strategy-indicator ${strategyClass}">${strategyName}</span>
        </div>
        <div class="status-item">
            <span class="status-label">Target Salary:</span>
            <span class="status-value">$${status.target_salary || 'Not set'}</span>
        </div>
        <div class="status-item">
            <span class="status-label">Current Offer:</span>
            <span class="status-value">${status.current_offer ? `$${status.current_offer.salary || 'N/A'}` : 'None'}</span>
        </div>
        <div class="status-item">
            <span class="status-label">Leverage Points:</span>
            <div class="leverage-points">
                ${status.leverage_points.map(point => 
                    `<span class="leverage-badge">${point.replace('_', ' ')}</span>`
                ).join('')}
            </div>
        </div>
        ${status.negotiation_history.length > 0 ? `
            <div class="mt-3">
                <h6>Negotiation History</h6>
                <div class="negotiation-history">
                    ${status.negotiation_history.slice(-5).map(entry => `
                        <div class="history-item">
                            <div class="history-type">${entry.type.replace('_', ' ')}</div>
                            <div class="history-timestamp">${new Date(entry.timestamp).toLocaleString()}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        ` : ''}
    `;
}

function updateStrategy() {
    if (!currentContextId) {
        showAlert('No active negotiation context', 'warning');
        return;
    }
    
    const strategy = document.getElementById('strategySelect').value;
    
    fetch('/api/update_strategy', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            context_id: currentContextId,
            strategy: strategy
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Strategy updated successfully!', 'success');
            loadNegotiationStatus();
        } else {
            showAlert(data.error || 'Failed to update strategy', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error updating strategy', 'danger');
    });
}

function showNegotiationSection() {
    document.getElementById('negotiationSection').style.display = 'block';
    document.getElementById('negotiationSection').scrollIntoView({ behavior: 'smooth' });
}

function showLoading() {
    const modal = new bootstrap.Modal(document.getElementById('loadingModal'));
    modal.show();
}

function hideLoading() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('loadingModal'));
    if (modal) {
        modal.hide();
    }
}

function showAlert(message, type) {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

// Example negotiation scenarios
function loadExampleScenario() {
    document.getElementById('companyName').value = 'TechCorp Inc';
    document.getElementById('position').value = 'Senior Product Manager';
    document.getElementById('yearsExperience').value = '7';
    document.getElementById('industry').value = 'technology';
    document.getElementById('educationLevel').value = 'Masters';
    document.getElementById('keyAchievement').value = 'Led team that increased revenue by 150%';
    document.getElementById('primarySkill').value = 'Product Management';
    document.getElementById('targetSalary').value = '120000';
    document.getElementById('targetBenefits').value = 'health insurance, 401k, stock options';
    document.getElementById('dealBreakers').value = 'no remote work, salary below 100k';
}

// Add example button (optional)
document.addEventListener('DOMContentLoaded', function() {
    const setupCard = document.querySelector('.card-header');
    const exampleButton = document.createElement('button');
    exampleButton.className = 'btn btn-outline-light btn-sm ms-2';
    exampleButton.innerHTML = '<i class="fas fa-magic me-1"></i>Load Example';
    exampleButton.onclick = loadExampleScenario;
    setupCard.appendChild(exampleButton);
});
