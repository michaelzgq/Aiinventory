/**
 * Inventory AI - Natural Language Query Interface
 * Handles voice input, query processing, and result display
 */

class NLQInterface {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this.lastQuery = '';
        
        this.initializeVoiceRecognition();
        this.initializeInterface();
    }
    
    initializeVoiceRecognition() {
        // Check for Web Speech API support
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';
            
            // Add Chinese support
            this.recognition.lang = 'en-US,zh-CN';
            
            this.recognition.onstart = () => {
                console.log('Voice recognition started');
                this.setListeningState(true);
            };
            
            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                console.log('Voice input received:', transcript);
                this.processVoiceInput(transcript);
            };
            
            this.recognition.onerror = (event) => {
                console.error('Voice recognition error:', event.error);
                this.showError(`Voice recognition error: ${event.error}`);
                this.setListeningState(false);
            };
            
            this.recognition.onend = () => {
                console.log('Voice recognition ended');
                this.setListeningState(false);
            };
        } else {
            console.log('Web Speech API not supported');
        }
    }
    
    initializeInterface() {
        // Example queries for user guidance
        this.exampleQueries = [
            "A54现在有什么？",
            "What's in bin A54?",
            "找 SKU-5566",
            "Where is PALT-0001?",
            "今天有多少异常",
            "Export today's report",
            "库存总览"
        ];
        
        this.setupExampleQueries();
    }
    
    setupExampleQueries() {
        const container = document.getElementById('example-queries');
        if (!container) return;
        
        const html = this.exampleQueries.map(query => `
            <button class="btn btn-outline-secondary btn-sm me-2 mb-2" onclick="nlqInterface.setQuery('${query}')">
                ${query}
            </button>
        `).join('');
        
        container.innerHTML = html;
    }
    
    startVoiceInput() {
        if (!this.recognition) {
            this.showError('Voice input not supported in this browser');
            return;
        }
        
        if (this.isListening) {
            this.stopVoiceInput();
            return;
        }
        
        try {
            this.recognition.start();
        } catch (error) {
            console.error('Error starting voice recognition:', error);
            this.showError('Failed to start voice input');
        }
    }
    
    stopVoiceInput() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }
    }
    
    setListeningState(listening) {
        this.isListening = listening;
        
        const voiceButton = document.querySelector('.voice-input-btn');
        if (voiceButton) {
            if (listening) {
                voiceButton.classList.add('voice-recording');
                voiceButton.innerHTML = '<i class="fas fa-stop"></i> Stop';
            } else {
                voiceButton.classList.remove('voice-recording');
                voiceButton.innerHTML = '<i class="fas fa-microphone"></i> Voice';
            }
        }
    }
    
    processVoiceInput(transcript) {
        const input = document.getElementById('nlq-input');
        if (input) {
            input.value = transcript;
            this.processQuery(transcript);
        }
    }
    
    setQuery(query) {
        const input = document.getElementById('nlq-input');
        if (input) {
            input.value = query;
            input.focus();
        }
    }
    
    async processQuery(query = null) {
        const input = document.getElementById('nlq-input');
        const resultContainer = document.getElementById('nlq-result');
        
        if (!query) {
            query = input?.value?.trim();
        }
        
        if (!query) {
            this.showError('Please enter a question');
            return;
        }
        
        this.lastQuery = query;
        
        // Show loading state
        if (resultContainer) {
            resultContainer.innerHTML = `
                <div class="d-flex align-items-center">
                    <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                    <span>Processing query...</span>
                </div>
            `;
        }
        
        try {
            const response = await fetch('/api/nlq/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getApiKey()}`
                },
                body: JSON.stringify({ text: query })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.displayResult(data);
                this.speakResult(data.answer);
            } else {
                throw new Error(data.detail || 'Query processing failed');
            }
            
        } catch (error) {
            console.error('NLQ processing error:', error);
            this.showError(`Error processing query: ${error.message}`);
            
            if (resultContainer) {
                resultContainer.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle"></i>
                        Error: ${error.message}
                    </div>
                `;
            }
        }
    }
    
    displayResult(data) {
        const resultContainer = document.getElementById('nlq-result');
        if (!resultContainer) return;
        
        let html = `
            <div class="alert alert-success">
                <h6><i class="fas fa-robot"></i> Answer:</h6>
                <p class="mb-0">${data.answer}</p>
            </div>
        `;
        
        if (data.data) {
            // Format structured data based on type
            if (data.data.bin_id) {
                html += this.formatBinData(data.data);
            } else if (data.data.sku) {
                html += this.formatSkuData(data.data);
            } else if (data.data.item_id) {
                html += this.formatItemData(data.data);
            } else if (data.data.total_anomalies !== undefined) {
                html += this.formatAnomalyData(data.data);
            } else {
                // Generic JSON display
                html += `
                    <div class="mt-3">
                        <h6>Additional Data:</h6>
                        <pre class="bg-light p-3 rounded small">${JSON.stringify(data.data, null, 2)}</pre>
                    </div>
                `;
            }
        }
        
        resultContainer.innerHTML = html;
    }
    
    formatBinData(data) {
        return `
            <div class="card mt-3">
                <div class="card-header">
                    <h6><i class="fas fa-cube"></i> Bin ${data.bin_id}</h6>
                </div>
                <div class="card-body">
                    <p><strong>Items:</strong> ${data.items.length}</p>
                    ${data.items.length > 0 ? `
                        <div class="mb-2">
                            ${data.items.map(item => `<span class="badge bg-primary me-1">${item}</span>`).join('')}
                        </div>
                    ` : '<p class="text-muted">No items detected</p>'}
                    ${data.photo_url ? `
                        <div class="mt-2">
                            <a href="${data.photo_url}" target="_blank" class="btn btn-sm btn-outline-info">
                                <i class="fas fa-image"></i> View Photo
                            </a>
                        </div>
                    ` : ''}
                    <small class="text-muted">
                        Last scanned: ${new Date(data.last_scanned).toLocaleString()}
                        | Confidence: ${(data.confidence * 100).toFixed(0)}%
                    </small>
                </div>
            </div>
        `;
    }
    
    formatSkuData(data) {
        return `
            <div class="card mt-3">
                <div class="card-header">
                    <h6><i class="fas fa-barcode"></i> SKU ${data.sku}</h6>
                </div>
                <div class="card-body">
                    <p><strong>Total Items:</strong> ${data.total_items}</p>
                    <p><strong>Found Items:</strong> ${data.found_items}</p>
                    
                    ${data.locations.length > 0 ? `
                        <div class="table-responsive">
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>Item ID</th>
                                        <th>Expected Bin</th>
                                        <th>Actual Bin</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${data.locations.map(loc => `
                                        <tr>
                                            <td>${loc.item_id}</td>
                                            <td>${loc.expected_bin || '-'}</td>
                                            <td>${loc.actual_bin || '-'}</td>
                                            <td>
                                                <span class="badge bg-${loc.status === 'found' ? 'success' : 'warning'}">
                                                    ${loc.status}
                                                </span>
                                            </td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    ` : '<p class="text-muted">No location data available</p>'}
                </div>
            </div>
        `;
    }
    
    formatItemData(data) {
        return `
            <div class="card mt-3">
                <div class="card-header">
                    <h6><i class="fas fa-tag"></i> Item ${data.item_id}</h6>
                </div>
                <div class="card-body">
                    <p><strong>SKU:</strong> ${data.sku}</p>
                    <p><strong>Expected Bin:</strong> ${data.expected_bin || 'Not allocated'}</p>
                    <p><strong>Actual Bin:</strong> ${data.actual_bin || 'Not found'}</p>
                    
                    ${data.photo_url ? `
                        <div class="mt-2">
                            <a href="${data.photo_url}" target="_blank" class="btn btn-sm btn-outline-info">
                                <i class="fas fa-image"></i> View Photo
                            </a>
                        </div>
                    ` : ''}
                    
                    ${data.last_seen ? `
                        <small class="text-muted">
                            Last seen: ${new Date(data.last_seen).toLocaleString()}
                        </small>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    formatAnomalyData(data) {
        return `
            <div class="card mt-3">
                <div class="card-header">
                    <h6><i class="fas fa-exclamation-triangle"></i> Anomalies for ${data.date}</h6>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6>By Severity:</h6>
                            ${Object.entries(data.by_severity || {}).map(([severity, count]) => `
                                <div class="d-flex justify-content-between">
                                    <span class="badge bg-${this.getSeverityColor(severity)}">${severity}</span>
                                    <span>${count}</span>
                                </div>
                            `).join('')}
                        </div>
                        <div class="col-md-6">
                            <h6>By Type:</h6>
                            ${Object.entries(data.by_type || {}).map(([type, count]) => `
                                <div class="d-flex justify-content-between small">
                                    <span>${type}</span>
                                    <span>${count}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    getSeverityColor(severity) {
        const colors = {
            'high': 'danger',
            'med': 'warning',
            'low': 'info'
        };
        return colors[severity] || 'secondary';
    }
    
    speakResult(text) {
        if ('speechSynthesis' in window) {
            // Cancel any ongoing speech
            speechSynthesis.cancel();
            
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            utterance.volume = 0.8;
            
            // Try to use Chinese voice for Chinese text
            if (/[\u4e00-\u9fff]/.test(text)) {
                const voices = speechSynthesis.getVoices();
                const chineseVoice = voices.find(voice => voice.lang.includes('zh'));
                if (chineseVoice) {
                    utterance.voice = chineseVoice;
                }
            }
            
            speechSynthesis.speak(utterance);
        }
    }
    
    showError(message) {
        if (typeof NotificationSystem !== 'undefined') {
            NotificationSystem.error(message);
        } else {
            console.error(message);
            alert(message);
        }
    }
    
    getApiKey() {
        return 'changeme-supersecret';
    }
    
    // Utility method to retry query
    retryLastQuery() {
        if (this.lastQuery) {
            this.processQuery(this.lastQuery);
        }
    }
}

// Initialize global NLQ interface
let nlqInterface;

document.addEventListener('DOMContentLoaded', function() {
    nlqInterface = new NLQInterface();
    
    // Setup keyboard shortcuts
    const nlqInput = document.getElementById('nlq-input');
    if (nlqInput) {
        nlqInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                nlqInterface.processQuery();
            }
        });
    }
    
    // Setup voice button if exists
    const voiceButton = document.querySelector('.voice-input-btn');
    if (voiceButton) {
        voiceButton.addEventListener('click', function() {
            nlqInterface.startVoiceInput();
        });
    }
});

// Global functions for template use
function processNLQ() {
    if (nlqInterface) {
        nlqInterface.processQuery();
    }
}

function startVoiceInput() {
    if (nlqInterface) {
        nlqInterface.startVoiceInput();
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { NLQInterface };
}