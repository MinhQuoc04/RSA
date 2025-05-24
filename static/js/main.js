// Main JavaScript for Secure File Transfer Application

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    initializeFileUpload();
    initializeFormValidation();
    initializeStatusPolling();
    initializeTooltips();
}

// File Upload Functionality
function initializeFileUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const uploadContent = uploadArea?.querySelector('.upload-content');

    if (!uploadArea || !fileInput) return;

    // Click to browse
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // File input change
    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleFileDrop);

    function handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            displayFileInfo(file);
        }
    }

    function handleDragOver(e) {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    }

    function handleDragLeave(e) {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
    }

    function handleFileDrop(e) {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            
            // Set the file to the input
            const dt = new DataTransfer();
            dt.items.add(file);
            fileInput.files = dt.files;
            
            displayFileInfo(file);
        }
    }

    function displayFileInfo(file) {
        if (!fileInfo || !uploadContent) return;

        // Validate file type
        const allowedTypes = [
            'text/plain', 'application/pdf', 'image/png', 'image/jpeg', 
            'image/gif', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/zip', 'application/x-tar', 'application/gzip'
        ];

        const fileExtension = file.name.split('.').pop().toLowerCase();
        const allowedExtensions = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'zip', 'tar', 'gz'];

        if (!allowedExtensions.includes(fileExtension)) {
            showAlert('File type not allowed. Please select a valid file type.', 'danger');
            return;
        }

        // Validate file size (16MB max)
        const maxSize = 16 * 1024 * 1024;
        if (file.size > maxSize) {
            showAlert('File too large. Maximum size is 16MB.', 'danger');
            return;
        }

        // Update UI
        uploadContent.style.display = 'none';
        fileInfo.style.display = 'block';
        uploadArea.classList.add('has-file');

        const fileName = fileInfo.querySelector('.file-name');
        const fileSize = fileInfo.querySelector('.file-size');

        if (fileName) fileName.textContent = file.name;
        if (fileSize) fileSize.textContent = formatFileSize(file.size);

        // Add remove file functionality
        fileInfo.addEventListener('click', removeFile);
    }

    function removeFile() {
        if (!fileInfo || !uploadContent) return;

        fileInput.value = '';
        fileInfo.style.display = 'none';
        uploadContent.style.display = 'block';
        uploadArea.classList.remove('has-file');
    }
}

// Form Validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                return false;
            }
            
            // Add loading state
            addLoadingState(this);
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });

    // Validate port numbers
    const portFields = form.querySelectorAll('input[type="number"]');
    portFields.forEach(field => {
        const port = parseInt(field.value);
        if (port < 1 || port > 65535) {
            showFieldError(field, 'Port must be between 1 and 65535');
            isValid = false;
        }
    });

    return isValid;
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    field.classList.add('is-invalid');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.classList.remove('is-invalid');
    
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

// Status Polling
function initializeStatusPolling() {
    // Check if there's an active transfer
    const transferStatus = document.querySelector('.status-card');
    if (transferStatus) {
        const isActive = transferStatus.querySelector('.fa-spinner');
        if (isActive) {
            // Poll status every 2 seconds
            const intervalId = setInterval(() => {
                fetch('/status')
                    .then(response => response.json())
                    .then(data => {
                        if (!data.active) {
                            // Transfer completed, reload page
                            clearInterval(intervalId);
                            setTimeout(() => {
                                window.location.reload();
                            }, 1000);
                        }
                    })
                    .catch(error => {
                        console.error('Error polling status:', error);
                        clearInterval(intervalId);
                    });
            }, 2000);
        }
    }
}

// Tooltips
function initializeTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Utility Functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function addLoadingState(form) {
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;
        
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
        
        // Remove loading state after 5 seconds as fallback
        setTimeout(() => {
            removeLoadingState(submitBtn, originalText);
        }, 5000);
    }
}

function removeLoadingState(btn, originalText) {
    btn.classList.remove('loading');
    btn.disabled = false;
    btn.innerHTML = originalText;
}

function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.container');
    if (!alertContainer) return;

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // Insert after navbar
    const navbar = document.querySelector('.navbar');
    if (navbar && navbar.nextElementSibling) {
        navbar.nextElementSibling.insertBefore(alertDiv, navbar.nextElementSibling.firstChild);
    } else {
        alertContainer.insertBefore(alertDiv, alertContainer.firstChild);
    }

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Network Status Indicator
function checkNetworkStatus() {
    const statusIndicator = document.createElement('div');
    statusIndicator.className = 'position-fixed bottom-0 end-0 m-3';
    statusIndicator.style.zIndex = '9999';
    
    function updateStatus() {
        if (navigator.onLine) {
            statusIndicator.innerHTML = `
                <div class="badge bg-success">
                    <i class="fas fa-wifi me-1"></i>Online
                </div>
            `;
        } else {
            statusIndicator.innerHTML = `
                <div class="badge bg-danger">
                    <i class="fas fa-wifi-slash me-1"></i>Offline
                </div>
            `;
        }
    }

    window.addEventListener('online', updateStatus);
    window.addEventListener('offline', updateStatus);
    
    updateStatus();
    document.body.appendChild(statusIndicator);
}

// Initialize network status on load
document.addEventListener('DOMContentLoaded', checkNetworkStatus);

// Keyboard Shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + R to refresh status
    if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        e.preventDefault();
        window.location.reload();
    }
    
    // Escape to clear file selection
    if (e.key === 'Escape') {
        const fileInput = document.getElementById('fileInput');
        const uploadArea = document.getElementById('uploadArea');
        
        if (fileInput && fileInput.files.length > 0) {
            fileInput.value = '';
            
            const fileInfo = document.getElementById('fileInfo');
            const uploadContent = uploadArea?.querySelector('.upload-content');
            
            if (fileInfo && uploadContent) {
                fileInfo.style.display = 'none';
                uploadContent.style.display = 'block';
                uploadArea.classList.remove('has-file');
            }
        }
    }
});

// Auto-scroll to status when transfer starts
function scrollToStatus() {
    const statusCard = document.querySelector('.status-card');
    if (statusCard) {
        statusCard.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'nearest' 
        });
    }
}

// Call scroll function if status is active
document.addEventListener('DOMContentLoaded', function() {
    const activeTransfer = document.querySelector('.fa-spinner');
    if (activeTransfer) {
        setTimeout(scrollToStatus, 500);
    }
});
