/**
 * Inventory AI - Scanning Interface
 * Handles camera preview, QR code detection, and image capture
 */

class ScanInterface {
    constructor() {
        this.video = document.getElementById('camera-preview');
        this.canvas = document.getElementById('capture-canvas');
        this.context = this.canvas.getContext('2d');
        this.stream = null;
        this.mode = 'bin'; // 'bin' or 'item'
        this.isScanning = false;
        this.codeReader = null;
        this.lastDetectedCodes = [];
        
        // Callbacks
        this.onLiveDetection = null;
        this.onCaptureResult = null;
        
        this.initializeInterface();
        this.initializeQRReader();
    }
    
    initializeInterface() {
        // Button event listeners
        document.getElementById('start-camera').addEventListener('click', () => this.startCamera());
        document.getElementById('stop-camera').addEventListener('click', () => this.stopCamera());
        document.getElementById('capture-photo').addEventListener('click', () => this.capturePhoto());
        document.getElementById('multi-capture').addEventListener('click', () => this.multiCapture());
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space' && this.isScanning) {
                e.preventDefault();
                this.capturePhoto();
            }
        });
    }
    
    initializeQRReader() {
        // Initialize ZXing QR code reader if available
        if (typeof ZXing !== 'undefined') {
            this.codeReader = new ZXing.BrowserMultiFormatReader();
            console.log('ZXing QR code reader initialized');
        }
    }
    
    async startCamera() {
        try {
            // Request camera access
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: 'environment' // Use rear camera if available
                }
            });
            
            this.video.srcObject = this.stream;
            this.video.addClass = 'active';
            this.isScanning = true;
            
            // Update UI
            this.updateUIState(true);
            
            // Start live QR detection
            this.startLiveDetection();
            
            console.log('Camera started successfully');
            
        } catch (error) {
            console.error('Error starting camera:', error);
            this.showError('Failed to start camera. Please check permissions.');
        }
    }
    
    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        
        this.video.srcObject = null;
        this.video.removeClass = 'active';
        this.isScanning = false;
        
        // Update UI
        this.updateUIState(false);
        
        // Stop live detection
        this.stopLiveDetection();
        
        console.log('Camera stopped');
    }
    
    updateUIState(isActive) {
        const startBtn = document.getElementById('start-camera');
        const stopBtn = document.getElementById('stop-camera');
        const captureBtn = document.getElementById('capture-photo');
        const multiBtn = document.getElementById('multi-capture');
        
        startBtn.disabled = isActive;
        stopBtn.disabled = !isActive;
        captureBtn.disabled = !isActive;
        multiBtn.disabled = !isActive;
    }
    
    startLiveDetection() {
        if (!this.codeReader || this.mode !== 'item') return;
        
        // Start continuous QR code scanning
        this.codeReader.decodeFromVideoDevice(undefined, this.video, (result, err) => {
            if (result) {
                const code = result.text;
                if (!this.lastDetectedCodes.includes(code)) {
                    this.lastDetectedCodes.push(code);
                    if (this.lastDetectedCodes.length > 10) {
                        this.lastDetectedCodes.shift(); // Keep only last 10
                    }
                }
                
                // Update live detection display
                if (this.onLiveDetection) {
                    this.onLiveDetection(this.lastDetectedCodes);
                }
            }
        });
    }
    
    stopLiveDetection() {
        if (this.codeReader) {
            this.codeReader.reset();
        }
        this.lastDetectedCodes = [];
    }
    
    capturePhoto() {
        if (!this.isScanning) return;
        
        // Set canvas size to match video
        this.canvas.width = this.video.videoWidth;
        this.canvas.height = this.video.videoHeight;
        
        // Draw current video frame to canvas
        this.context.drawImage(this.video, 0, 0);
        
        // Convert to blob and upload
        this.canvas.toBlob((blob) => {
            this.uploadImage(blob);
        }, 'image/jpeg', 0.8);
        
        // Visual feedback
        this.flashCapture();
    }
    
    async multiCapture() {
        if (!this.isScanning) return;
        
        const captureBtn = document.getElementById('multi-capture');
        const originalText = captureBtn.innerHTML;
        
        captureBtn.disabled = true;
        
        const images = [];
        const captureCount = 3;
        const interval = 500; // ms between captures
        
        for (let i = 0; i < captureCount; i++) {
            captureBtn.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Capturing ${i + 1}/${captureCount}`;
            
            // Capture frame
            this.canvas.width = this.video.videoWidth;
            this.canvas.height = this.video.videoHeight;
            this.context.drawImage(this.video, 0, 0);
            
            const blob = await this.canvasToBlob();
            images.push(blob);
            
            // Visual feedback
            this.flashCapture();
            
            // Wait between captures
            if (i < captureCount - 1) {
                await this.sleep(interval);
            }
        }
        
        // Upload multiple images
        this.uploadMultipleImages(images);
        
        captureBtn.innerHTML = originalText;
        captureBtn.disabled = false;
    }
    
    canvasToBlob() {
        return new Promise((resolve) => {
            this.canvas.toBlob(resolve, 'image/jpeg', 0.8);
        });
    }
    
    flashCapture() {
        // Create flash effect
        const flash = document.createElement('div');
        flash.style.position = 'fixed';
        flash.style.top = '0';
        flash.style.left = '0';
        flash.style.width = '100vw';
        flash.style.height = '100vh';
        flash.style.backgroundColor = 'white';
        flash.style.opacity = '0.8';
        flash.style.zIndex = '9999';
        flash.style.pointerEvents = 'none';
        
        document.body.appendChild(flash);
        
        setTimeout(() => {
            document.body.removeChild(flash);
        }, 100);
    }
    
    async uploadImage(blob) {
        try {
            const formData = new FormData();
            formData.append('image', blob, 'snapshot.jpg');
            
            // Add optional fields
            const binId = document.getElementById('manual-bin-id').value.trim();
            const notes = document.getElementById('capture-notes').value.trim();
            
            if (binId) formData.append('bin_id', binId);
            if (notes) formData.append('notes', notes);
            
            const response = await fetch('/api/snapshots/upload', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.getApiKey()}`
                },
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                console.log('Upload successful:', result);
                if (this.onCaptureResult) {
                    this.onCaptureResult(result);
                }
            } else {
                throw new Error(result.detail || 'Upload failed');
            }
            
        } catch (error) {
            console.error('Upload error:', error);
            this.showError(`Upload failed: ${error.message}`);
        }
    }
    
    async uploadMultipleImages(images) {
        try {
            const formData = new FormData();
            
            images.forEach((blob, index) => {
                formData.append('images', blob, `snapshot_${index}.jpg`);
            });
            
            // Add optional fields
            const binId = document.getElementById('manual-bin-id').value.trim();
            const notes = document.getElementById('capture-notes').value.trim();
            
            if (binId) formData.append('bin_id', binId);
            if (notes) formData.append('notes', notes);
            
            const response = await fetch('/api/snapshots/upload-multiple', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.getApiKey()}`
                },
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                console.log('Multi-upload successful:', result);
                if (this.onCaptureResult) {
                    this.onCaptureResult(result);
                }
            } else {
                throw new Error(result.detail || 'Multi-upload failed');
            }
            
        } catch (error) {
            console.error('Multi-upload error:', error);
            this.showError(`Multi-upload failed: ${error.message}`);
        }
    }
    
    setMode(mode) {
        this.mode = mode;
        console.log(`Scan mode set to: ${mode}`);
        
        // Restart live detection if camera is active
        if (this.isScanning) {
            this.stopLiveDetection();
            this.startLiveDetection();
        }
    }
    
    showError(message) {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white bg-danger border-0';
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        // Add to toast container (create if doesn't exist)
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(container);
        }
        
        container.appendChild(toast);
        
        // Show toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove from DOM after hiding
        toast.addEventListener('hidden.bs.toast', () => {
            container.removeChild(toast);
        });
    }
    
    getApiKey() {
        // In a real app, this would be more secure
        return 'changeme-supersecret';
    }
    
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Utility functions for file upload drag & drop
function initializeFileUpload() {
    const dropZones = document.querySelectorAll('.file-drop-zone');
    
    dropZones.forEach(zone => {
        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            zone.classList.add('dragover');
        });
        
        zone.addEventListener('dragleave', () => {
            zone.classList.remove('dragover');
        });
        
        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            zone.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                // Handle dropped files
                handleDroppedFiles(files);
            }
        });
    });
}

function handleDroppedFiles(files) {
    Array.from(files).forEach(file => {
        if (file.type.startsWith('image/')) {
            // Process image file
            console.log('Processing dropped image:', file.name);
            // Add file processing logic here
        }
    });
}

// Notification system
class NotificationSystem {
    static show(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(container);
        }
        
        container.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast, { delay: duration });
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', () => {
            if (container.contains(toast)) {
                container.removeChild(toast);
            }
        });
    }
    
    static success(message) {
        this.show(message, 'success');
    }
    
    static error(message) {
        this.show(message, 'danger', 8000);
    }
    
    static warning(message) {
        this.show(message, 'warning');
    }
    
    static info(message) {
        this.show(message, 'info');
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    initializeFileUpload();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ScanInterface, NotificationSystem };
}