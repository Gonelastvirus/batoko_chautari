/**
 * Batoko Chautari - Main JavaScript File
 * Nepal Nature Discovery Platform
 * 
 * This file contains all the core JavaScript functionality
 * for the Batoko Chautari web application.
 */

'use strict';

// ========================================
// Global Configuration and Constants
// ========================================

const BatokoChautari = {
    config: {
        animationDuration: 300,
        debounceDelay: 250,
        apiTimeout: 10000,
        maxFileSize: 16 * 1024 * 1024, // 16MB
        allowedImageTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
        weatherUpdateInterval: 300000, // 5 minutes
    },
    
    state: {
        isLoading: false,
        currentUser: null,
        theme: 'light',
        notifications: [],
    },
    
    // Utility functions
    utils: {},
    
    // Feature modules
    modules: {}
};

// ========================================
// Utility Functions
// ========================================

BatokoChautari.utils = {
    /**
     * Debounce function to limit API calls
     */
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Throttle function for scroll events
     */
    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    /**
     * Format file size in human readable format
     */
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    /**
     * Generate random ID
     */
    generateId: function() {
        return Math.random().toString(36).substr(2, 9);
    },

    /**
     * Validate email format
     */
    isValidEmail: function(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    /**
     * Sanitize HTML to prevent XSS
     */
    sanitizeHtml: function(str) {
        const temp = document.createElement('div');
        temp.textContent = str;
        return temp.innerHTML;
    },

    /**
     * Format date in a readable format
     */
    formatDate: function(date) {
        if (!(date instanceof Date)) {
            date = new Date(date);
        }
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },

    /**
     * Copy text to clipboard
     */
    copyToClipboard: function(text) {
        if (navigator.clipboard) {
            return navigator.clipboard.writeText(text);
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            try {
                document.execCommand('copy');
                document.body.removeChild(textArea);
                return Promise.resolve();
            } catch (err) {
                document.body.removeChild(textArea);
                return Promise.reject(err);
            }
        }
    },

    /**
     * Get cookie value by name
     */
    getCookie: function(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    },

    /**
     * Show loading indicator
     */
    showLoading: function(element) {
        if (element) {
            element.classList.add('loading');
        }
        BatokoChautari.state.isLoading = true;
    },

    /**
     * Hide loading indicator
     */
    hideLoading: function(element) {
        if (element) {
            element.classList.remove('loading');
        }
        BatokoChautari.state.isLoading = false;
    }
};

// ========================================
// Notification System
// ========================================

BatokoChautari.modules.notifications = {
    container: null,

    init: function() {
        this.createContainer();
    },

    createContainer: function() {
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'notification-container';
            this.container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                max-width: 400px;
            `;
            document.body.appendChild(this.container);
        }
    },

    show: function(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        const id = BatokoChautari.utils.generateId();
        
        notification.id = `notification-${id}`;
        notification.className = `alert alert-${type} alert-dismissible fade show notification-item`;
        notification.style.cssText = `
            margin-bottom: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            border: none;
            border-radius: 8px;
        `;

        const iconMap = {
            'success': 'fas fa-check-circle',
            'error': 'fas fa-exclamation-circle',
            'warning': 'fas fa-exclamation-triangle',
            'info': 'fas fa-info-circle'
        };

        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="${iconMap[type] || iconMap.info} me-2"></i>
                <span>${BatokoChautari.utils.sanitizeHtml(message)}</span>
                <button type="button" class="btn-close ms-auto" onclick="BatokoChautari.modules.notifications.hide('${id}')"></button>
            </div>
        `;

        this.container.appendChild(notification);
        
        // Auto-hide after duration
        if (duration > 0) {
            setTimeout(() => {
                this.hide(id);
            }, duration);
        }

        // Add to state
        BatokoChautari.state.notifications.push({
            id: id,
            message: message,
            type: type,
            timestamp: new Date()
        });

        return id;
    },

    hide: function(id) {
        const notification = document.getElementById(`notification-${id}`);
        if (notification) {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 150);
        }

        // Remove from state
        BatokoChautari.state.notifications = BatokoChautari.state.notifications.filter(
            n => n.id !== id
        );
    },

    success: function(message, duration = 5000) {
        return this.show(message, 'success', duration);
    },

    error: function(message, duration = 8000) {
        return this.show(message, 'danger', duration);
    },

    warning: function(message, duration = 6000) {
        return this.show(message, 'warning', duration);
    },

    info: function(message, duration = 5000) {
        return this.show(message, 'info', duration);
    }
};

// ========================================
// Image Handling Module
// ========================================

BatokoChautari.modules.imageHandler = {
    init: function() {
        this.setupImageLazyLoading();
        this.setupImageErrorHandling();
        this.setupImagePreview();
    },

    setupImageLazyLoading: function() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);
                    }
                });
            });

            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
    },

    setupImageErrorHandling: function() {
        document.addEventListener('error', function(e) {
            if (e.target.tagName === 'IMG') {
                e.target.src = '/static/images/placeholder.jpg';
                e.target.alt = 'Image not available';
            }
        }, true);
    },

    setupImagePreview: function() {
        // Handle image modal previews
        document.addEventListener('click', function(e) {
            if (e.target.hasAttribute('data-bs-toggle') && 
                e.target.getAttribute('data-bs-toggle') === 'modal') {
                const modalId = e.target.getAttribute('data-bs-target');
                const modal = document.querySelector(modalId);
                if (modal) {
                    const img = modal.querySelector('img');
                    const caption = modal.querySelector('.modal-caption');
                    
                    if (img) {
                        img.src = e.target.getAttribute('data-bs-img') || e.target.src;
                    }
                    if (caption) {
                        caption.textContent = e.target.getAttribute('data-bs-caption') || '';
                    }
                }
            }
        });
    },

    validateFile: function(file) {
        const errors = [];

        // Check file type
        if (!BatokoChautari.config.allowedImageTypes.includes(file.type)) {
            errors.push('Invalid file type. Please upload JPG, PNG, GIF, or WebP images only.');
        }

        // Check file size
        if (file.size > BatokoChautari.config.maxFileSize) {
            errors.push(`File size too large. Maximum size is ${BatokoChautari.utils.formatFileSize(BatokoChautari.config.maxFileSize)}.`);
        }

        return {
            valid: errors.length === 0,
            errors: errors
        };
    },

    createThumbnail: function(file, maxWidth = 300, maxHeight = 300) {
        return new Promise((resolve, reject) => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();

            img.onload = function() {
                // Calculate new dimensions
                let { width, height } = img;
                
                if (width > height) {
                    if (width > maxWidth) {
                        height = (height * maxWidth) / width;
                        width = maxWidth;
                    }
                } else {
                    if (height > maxHeight) {
                        width = (width * maxHeight) / height;
                        height = maxHeight;
                    }
                }

                canvas.width = width;
                canvas.height = height;

                // Draw resized image
                ctx.drawImage(img, 0, 0, width, height);

                // Convert to blob
                canvas.toBlob(resolve, 'image/jpeg', 0.8);
            };

            img.onerror = reject;
            img.src = URL.createObjectURL(file);
        });
    }
};

// ========================================
// Form Validation Module
// ========================================

BatokoChautari.modules.formValidation = {
    init: function() {
        this.setupRealTimeValidation();
        this.setupFormSubmission();
    },

    setupRealTimeValidation: function() {
        // Email validation
        document.addEventListener('input', function(e) {
            if (e.target.type === 'email') {
                const isValid = BatokoChautari.utils.isValidEmail(e.target.value);
                e.target.setCustomValidity(isValid ? '' : 'Please enter a valid email address');
                
                // Visual feedback
                if (e.target.value.length > 0) {
                    e.target.classList.toggle('is-valid', isValid);
                    e.target.classList.toggle('is-invalid', !isValid);
                } else {
                    e.target.classList.remove('is-valid', 'is-invalid');
                }
            }
        });

        // Password strength validation
        document.addEventListener('input', function(e) {
            if (e.target.type === 'password' && e.target.name === 'password') {
                const strength = BatokoChautari.modules.formValidation.checkPasswordStrength(e.target.value);
                const strengthIndicator = document.querySelector('#passwordStrengthBar');
                const strengthText = document.querySelector('#passwordStrengthText');
                
                if (strengthIndicator) {
                    strengthIndicator.style.width = `${strength.score * 25}%`;
                    strengthIndicator.className = `progress-bar ${strength.class}`;
                }
                
                if (strengthText) {
                    strengthText.textContent = strength.text;
                }
            }
        });

        // Password confirmation validation
        document.addEventListener('input', function(e) {
            if (e.target.name === 'password2' || e.target.name === 'password_confirm') {
                const passwordField = document.querySelector('input[name="password"]');
                const confirmField = e.target;
                
                if (passwordField && confirmField.value.length > 0) {
                    const matches = passwordField.value === confirmField.value;
                    confirmField.setCustomValidity(matches ? '' : 'Passwords do not match');
                    confirmField.classList.toggle('is-valid', matches);
                    confirmField.classList.toggle('is-invalid', !matches);
                }
            }
        });
    },

    setupFormSubmission: function() {
        document.addEventListener('submit', function(e) {
            const form = e.target;
            
            // Prevent double submission
            if (form.dataset.submitting === 'true') {
                e.preventDefault();
                return;
            }

            // Mark as submitting
            form.dataset.submitting = 'true';
            
            // Show loading state on submit button
            const submitBtn = form.querySelector('input[type="submit"], button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.textContent || submitBtn.value;
                submitBtn.disabled = true;
                
                if (submitBtn.tagName === 'BUTTON') {
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
                } else {
                    submitBtn.value = 'Processing...';
                }

                // Reset after timeout
                setTimeout(() => {
                    form.dataset.submitting = 'false';
                    submitBtn.disabled = false;
                    if (submitBtn.tagName === 'BUTTON') {
                        submitBtn.textContent = originalText;
                    } else {
                        submitBtn.value = originalText;
                    }
                }, 5000);
            }
        });
    },

    checkPasswordStrength: function(password) {
        let score = 0;
        let text = 'Too weak';
        let className = 'bg-danger';

        if (password.length >= 6) score++;
        if (password.match(/[a-z]/) && password.match(/[A-Z]/)) score++;
        if (password.match(/\d/)) score++;
        if (password.match(/[^a-zA-Z\d]/)) score++;

        switch (score) {
            case 0:
            case 1:
                text = 'Weak';
                className = 'bg-danger';
                break;
            case 2:
                text = 'Fair';
                className = 'bg-warning';
                break;
            case 3:
                text = 'Good';
                className = 'bg-info';
                break;
            case 4:
                text = 'Strong';
                className = 'bg-success';
                break;
        }

        return { score, text, class: className };
    }
};

// ========================================
// Search and Filter Module
// ========================================

BatokoChautari.modules.searchFilter = {
    init: function() {
        this.setupSearchDebouncing();
        this.setupFilterToggles();
        this.setupSortOptions();
    },

    setupSearchDebouncing: function() {
        const searchInputs = document.querySelectorAll('input[type="search"], input[name="search"]');
        
        searchInputs.forEach(input => {
            const debouncedSearch = BatokoChautari.utils.debounce(function() {
                // Auto-submit form or trigger search
                const form = input.closest('form');
                if (form) {
                    form.submit();
                }
            }, BatokoChautari.config.debounceDelay);

            input.addEventListener('input', debouncedSearch);
        });
    },

    setupFilterToggles: function() {
        // Toggle advanced filters
        const filterToggle = document.querySelector('#toggleFilters');
        const filterPanel = document.querySelector('#advancedFilters');
        
        if (filterToggle && filterPanel) {
            filterToggle.addEventListener('click', function() {
                filterPanel.classList.toggle('show');
                this.textContent = filterPanel.classList.contains('show') ? 
                    'Hide Filters' : 'Show Filters';
            });
        }
    },

    setupSortOptions: function() {
        const sortSelect = document.querySelector('select[name="sort"]');
        
        if (sortSelect) {
            sortSelect.addEventListener('change', function() {
                const form = this.closest('form');
                if (form) {
                    form.submit();
                }
            });
        }
    }
};

// ========================================
// Weather Module
// ========================================

BatokoChautari.modules.weather = {
    cache: new Map(),
    
    init: function() {
        this.loadWeatherData();
        this.setupPeriodicUpdates();
    },

    loadWeatherData: function() {
        const weatherWidgets = document.querySelectorAll('[data-weather-lat][data-weather-lon]');
        
        weatherWidgets.forEach(widget => {
            const lat = parseFloat(widget.dataset.weatherLat);
            const lon = parseFloat(widget.dataset.weatherLon);
            
            this.fetchWeather(lat, lon).then(data => {
                this.renderWeather(widget, data);
            }).catch(error => {
                console.error('Weather fetch failed:', error);
                widget.innerHTML = '<p class="text-muted">Weather data unavailable</p>';
            });
        });
    },

    fetchWeather: function(lat, lon) {
        const cacheKey = `${lat},${lon}`;
        const cached = this.cache.get(cacheKey);
        
        // Return cached data if it's less than 5 minutes old
        if (cached && (Date.now() - cached.timestamp) < 300000) {
            return Promise.resolve(cached.data);
        }

        return fetch(`/api/weather/${lat}/${lon}`)
            .then(response => response.json())
            .then(data => {
                this.cache.set(cacheKey, {
                    data: data,
                    timestamp: Date.now()
                });
                return data;
            });
    },

    renderWeather: function(widget, data) {
        if (!data || data.error) {
            widget.innerHTML = '<p class="text-muted">Weather data unavailable</p>';
            return;
        }

        const current = data.current;
        const forecast = data.forecast || [];

        widget.innerHTML = `
            <div class="weather-current text-center mb-3">
                <div class="d-flex align-items-center justify-content-center mb-2">
                    <img src="https://openweathermap.org/img/wn/${current.icon}@2x.png" 
                         alt="${current.description}" style="width: 50px;">
                    <span class="weather-temp ms-2">${current.temp}°C</span>
                </div>
                <p class="weather-desc mb-1">${current.description}</p>
                <div class="weather-details">
                    <span>💧 ${current.humidity}%</span>
                    <span>💨 ${current.wind_speed}m/s</span>
                </div>
            </div>
            ${forecast.length > 0 ? `
                <div class="weather-forecast">
                    ${forecast.map(day => `
                        <div class="forecast-day">
                            <small>${day.date}</small>
                            <img src="https://openweathermap.org/img/wn/${day.icon}.png" 
                                 alt="Weather" style="width: 30px;">
                            <small>${day.temp_max}°/${day.temp_min}°</small>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
        `;
    },

    setupPeriodicUpdates: function() {
        // Update weather data every 5 minutes
        setInterval(() => {
            this.loadWeatherData();
        }, BatokoChautari.config.weatherUpdateInterval);
    }
};

// ========================================
// Photo Gallery Module
// ========================================

BatokoChautari.modules.photoGallery = {
    init: function() {
        this.setupLightbox();
        this.setupLazyLoading();
        this.setupPhotoUpload();
    },

    setupLightbox: function() {
        // Enhanced modal functionality for photo galleries
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('gallery-img') || 
                e.target.classList.contains('photo-thumbnail')) {
                
                const modalId = e.target.getAttribute('data-bs-target');
                if (modalId) {
                    const modal = document.querySelector(modalId);
                    const modalImg = modal.querySelector('#modalImage, .modal-image');
                    const modalCaption = modal.querySelector('#modalCaption, .modal-caption');
                    
                    if (modalImg) {
                        modalImg.src = e.target.getAttribute('data-bs-img') || e.target.src;
                        modalImg.alt = e.target.alt;
                    }
                    
                    if (modalCaption) {
                        modalCaption.textContent = e.target.getAttribute('data-bs-caption') || e.target.alt;
                    }
                }
            }
        });
    },

    setupLazyLoading: function() {
        // Intersection Observer for lazy loading gallery images
        if ('IntersectionObserver' in window) {
            const galleryObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        const placeholder = img.src;
                        img.src = img.dataset.src || img.src;
                        img.classList.add('loaded');
                        galleryObserver.unobserve(img);
                    }
                });
            }, {
                rootMargin: '50px'
            });

            document.querySelectorAll('.gallery-img[data-src]').forEach(img => {
                galleryObserver.observe(img);
            });
        }
    },

    setupPhotoUpload: function() {
        const uploadAreas = document.querySelectorAll('.upload-area');
        
        uploadAreas.forEach(area => {
            const input = area.querySelector('input[type="file"]');
            
            if (!input) return;

            // Drag and drop functionality
            area.addEventListener('dragover', function(e) {
                e.preventDefault();
                this.classList.add('drag-over');
            });

            area.addEventListener('dragleave', function(e) {
                e.preventDefault();
                this.classList.remove('drag-over');
            });

            area.addEventListener('drop', function(e) {
                e.preventDefault();
                this.classList.remove('drag-over');
                
                const files = Array.from(e.dataTransfer.files);
                BatokoChautari.modules.photoGallery.handleFileSelection(files, input);
            });

            // Click to select files
            area.addEventListener('click', function(e) {
                if (e.target === area) {
                    input.click();
                }
            });

            input.addEventListener('change', function(e) {
                const files = Array.from(e.target.files);
                BatokoChautari.modules.photoGallery.handleFileSelection(files, input);
            });
        });
    },

    handleFileSelection: function(files, input) {
        const validFiles = [];
        const errors = [];

        files.forEach(file => {
            const validation = BatokoChautari.modules.imageHandler.validateFile(file);
            if (validation.valid) {
                validFiles.push(file);
            } else {
                errors.push(`${file.name}: ${validation.errors.join(', ')}`);
            }
        });

        if (errors.length > 0) {
            BatokoChautari.modules.notifications.error(
                'Some files were rejected:\n' + errors.join('\n')
            );
        }

        if (validFiles.length > 0) {
            this.showPhotoPreview(validFiles, input);
            BatokoChautari.modules.notifications.success(
                `${validFiles.length} photo(s) selected successfully`
            );
        }
    },

    showPhotoPreview: function(files, input) {
        const previewContainer = document.querySelector('#photoPreview, .photo-preview');
        if (!previewContainer) return;

        previewContainer.innerHTML = '';
        
        const grid = document.createElement('div');
        grid.className = 'row g-3';

        files.forEach((file, index) => {
            const col = document.createElement('div');
            col.className = 'col-md-3 col-6';

            const reader = new FileReader();
            reader.onload = function(e) {
                col.innerHTML = `
                    <div class="card border-0 shadow-sm position-relative">
                        <img src="${e.target.result}" class="card-img-top" 
                             style="height: 150px; object-fit: cover;" alt="${file.name}">
                        <button type="button" class="btn btn-danger btn-sm position-absolute top-0 end-0 m-2 rounded-circle"
                                onclick="this.closest('.col-md-3').remove()">
                            <i class="fas fa-times"></i>
                        </button>
                        <div class="card-body p-2">
                            <small class="text-muted">${file.name}</small>
                            <br>
                            <small class="text-muted">${BatokoChautari.utils.formatFileSize(file.size)}</small>
                        </div>
                    </div>
                `;
            };
            reader.readAsDataURL(file);

            grid.appendChild(col);
        });

        previewContainer.appendChild(grid);
    }
};

// ========================================
// Navigation and UI Module
// ========================================

BatokoChautari.modules.navigation = {
    init: function() {
        this.setupSmoothScrolling();
        this.setupBackToTop();
        this.setupMobileNavigation();
        this.setupDropdownMenus();
    },

    setupSmoothScrolling: function() {
        document.addEventListener('click', function(e) {
            if (e.target.hash && e.target.getAttribute('href').startsWith('#')) {
                e.preventDefault();
                const target = document.querySelector(e.target.hash);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    },

    setupBackToTop: function() {
        const backToTopBtn = document.createElement('button');
        backToTopBtn.innerHTML = '<i class="fas fa-chevron-up"></i>';
        backToTopBtn.className = 'btn btn-nature back-to-top';
        backToTopBtn.style.cssText = `
            position: fixed;
            bottom: 100px;
            right: 30px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: none;
            z-index: 999;
            transition: all 0.3s ease;
        `;

        backToTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });

        document.body.appendChild(backToTopBtn);

        // Show/hide based on scroll position
        const toggleBackToTop = BatokoChautari.utils.throttle(function() {
            if (window.scrollY > 300) {
                backToTopBtn.style.display = 'block';
            } else {
                backToTopBtn.style.display = 'none';
            }
        }, 100);

        window.addEventListener('scroll', toggleBackToTop);
    },

    setupMobileNavigation: function() {
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(e) {
            const navbarCollapse = document.querySelector('.navbar-collapse');
            const navbarToggler = document.querySelector('.navbar-toggler');
            
            if (navbarCollapse && navbarCollapse.classList.contains('show')) {
                if (!navbarCollapse.contains(e.target) && !navbarToggler.contains(e.target)) {
                    const collapseInstance = bootstrap.Collapse.getInstance(navbarCollapse);
                    if (collapseInstance) {
                        collapseInstance.hide();
                    }
                }
            }
        });
    },

    setupDropdownMenus: function() {
        // Enhanced dropdown functionality
        document.addEventListener('shown.bs.dropdown', function(e) {
            const dropdown = e.target;
            const menu = dropdown.nextElementSibling;
            
            // Adjust dropdown position if it goes off-screen
            const rect = menu.getBoundingClientRect();
            if (rect.right > window.innerWidth) {
                menu.classList.add('dropdown-menu-end');
            }
        });
    }
};

// ========================================
// Animation and Effects Module
// ========================================

BatokoChautari.modules.animations = {
    init: function() {
        this.setupScrollAnimations();
        this.setupHoverEffects();
        this.setupLoadingAnimations();
    },

    setupScrollAnimations: function() {
        if ('IntersectionObserver' in window) {
            const animationObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate-in');
                        animationObserver.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            });

            // Add animation classes to elements
            document.querySelectorAll('.card, .feature-card, .spot-card').forEach(el => {
                el.classList.add('animate-on-scroll');
                animationObserver.observe(el);
            });
        }
    },

    setupHoverEffects: function() {
        // Add hover effects to interactive elements
        document.querySelectorAll('.card, .btn, .nav-link').forEach(el => {
            el.addEventListener('mouseenter', function() {
                this.classList.add('hover-effect');
            });

            el.addEventListener('mouseleave', function() {
                this.classList.remove('hover-effect');
            });
        });
    },

    setupLoadingAnimations: function() {
        // Add loading states to buttons and forms
        document.addEventListener('submit', function(e) {
            const form = e.target;
            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
            
            if (submitBtn) {
                submitBtn.classList.add('loading');
            }
        });
    }
};

// ========================================
// Accessibility Module
// ========================================

BatokoChautari.modules.accessibility = {
    init: function() {
        this.setupKeyboardNavigation();
        this.setupFocusManagement();
        this.setupScreenReaderSupport();
    },

    setupKeyboardNavigation: function() {
        // Escape key to close modals
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                const openModals = document.querySelectorAll('.modal.show');
                openModals.forEach(modal => {
                    const modalInstance = bootstrap.Modal.getInstance(modal);
                    if (modalInstance) {
                        modalInstance.hide();
                    }
                });
            }
        });

        // Tab navigation improvements
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Tab') {
                document.body.classList.add('using-keyboard');
            }
        });

        document.addEventListener('mousedown', function() {
            document.body.classList.remove('using-keyboard');
        });
    },

    setupFocusManagement: function() {
        // Focus management for modals
        document.addEventListener('shown.bs.modal', function(e) {
            const modal = e.target;
            const focusable = modal.querySelector('input, button, select, textarea, [tabindex]:not([tabindex="-1"])');
            if (focusable) {
                focusable.focus();
            }
        });

        // Skip to main content link
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.textContent = 'Skip to main content';
        skipLink.className = 'skip-link';
        skipLink.style.cssText = `
            position: absolute;
            top: -40px;
            left: 6px;
            background: var(--forest-primary);
            color: white;
            padding: 8px;
            text-decoration: none;
            border-radius: 4px;
            z-index: 10000;
            transition: top 0.3s;
        `;

        skipLink.addEventListener('focus', function() {
            this.style.top = '6px';
        });

        skipLink.addEventListener('blur', function() {
            this.style.top = '-40px';
        });

        document.body.insertBefore(skipLink, document.body.firstChild);
    },

    setupScreenReaderSupport: function() {
        // Add ARIA labels to interactive elements without labels
        document.querySelectorAll('button:not([aria-label]):not([aria-labelledby])').forEach(btn => {
            if (!btn.textContent.trim()) {
                const icon = btn.querySelector('i');
                if (icon) {
                    btn.setAttribute('aria-label', this.getIconDescription(icon.className));
                }
            }
        });

        // Announce dynamic content changes
        this.createLiveRegion();
    },

    createLiveRegion: function() {
        const liveRegion = document.createElement('div');
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.style.cssText = `
            position: absolute;
            left: -10000px;
            width: 1px;
            height: 1px;
            overflow: hidden;
        `;
        document.body.appendChild(liveRegion);

        // Store reference for announcements
        BatokoChautari.modules.accessibility.liveRegion = liveRegion;
    },

    announce: function(message) {
        if (this.liveRegion) {
            this.liveRegion.textContent = message;
        }
    },

    getIconDescription: function(className) {
        const iconMap = {
            'fa-search': 'Search',
            'fa-user': 'User',
            'fa-home': 'Home',
            'fa-heart': 'Like',
            'fa-star': 'Star',
            'fa-bookmark': 'Bookmark',
            'fa-share': 'Share',
            'fa-edit': 'Edit',
            'fa-trash': 'Delete',
            'fa-plus': 'Add',
            'fa-minus': 'Remove',
            'fa-close': 'Close',
            'fa-menu': 'Menu'
        };

        for (const [iconClass, description] of Object.entries(iconMap)) {
            if (className.includes(iconClass)) {
                return description;
            }
        }

        return 'Button';
    }
};

// ========================================
// Performance Module
// ========================================

BatokoChautari.modules.performance = {
    init: function() {
        this.setupLazyLoading();
        this.setupImageOptimization();
        this.setupCaching();
        this.monitorPerformance();
    },

    setupLazyLoading: function() {
        // Lazy load non-critical content
        if ('IntersectionObserver' in window) {
            const lazyObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const element = entry.target;
                        
                        // Load deferred content
                        if (element.dataset.src) {
                            element.src = element.dataset.src;
                        }
                        
                        if (element.dataset.content) {
                            element.innerHTML = element.dataset.content;
                        }
                        
                        element.classList.remove('lazy');
                        lazyObserver.unobserve(element);
                    }
                });
            });

            document.querySelectorAll('.lazy').forEach(el => {
                lazyObserver.observe(el);
            });
        }
    },

    setupImageOptimization: function() {
        // Implement responsive images
        document.querySelectorAll('img').forEach(img => {
            if (!img.loading) {
                img.loading = 'lazy';
            }
        });
    },

    setupCaching: function() {
        // Service Worker registration for caching
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/sw.js')
                    .then(registration => {
                        console.log('SW registered: ', registration);
                    })
                    .catch(registrationError => {
                        console.log('SW registration failed: ', registrationError);
                    });
            });
        }
    },

    monitorPerformance: function() {
        // Performance monitoring
        window.addEventListener('load', () => {
            setTimeout(() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                if (perfData) {
                    console.log('Page load time:', perfData.loadEventEnd - perfData.fetchStart, 'ms');
                }
            }, 0);
        });
    }
};

// ========================================
// Application Initialization
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all modules
    Object.keys(BatokoChautari.modules).forEach(moduleKey => {
        const module = BatokoChautari.modules[moduleKey];
        if (typeof module.init === 'function') {
            try {
                module.init();
            } catch (error) {
                console.error(`Failed to initialize module ${moduleKey}:`, error);
            }
        }
    });

    // Set up global error handling
    window.addEventListener('error', function(e) {
        console.error('Global error:', e.error);
        BatokoChautari.modules.notifications.error(
            'An unexpected error occurred. Please refresh the page.'
        );
    });

    // Set up unhandled promise rejection handling
    window.addEventListener('unhandledrejection', function(e) {
        console.error('Unhandled promise rejection:', e.reason);
        BatokoChautari.modules.notifications.error(
            'A network error occurred. Please check your connection.'
        );
    });

    // Initialize tooltips and popovers
    if (typeof bootstrap !== 'undefined') {
        // Initialize Bootstrap tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });

        // Initialize Bootstrap popovers
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function(popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }

    console.log('Batoko Chautari application initialized successfully');
});

// ========================================
// Export for global access
// ========================================

window.BatokoChautari = BatokoChautari;
