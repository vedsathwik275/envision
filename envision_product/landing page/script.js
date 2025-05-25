// Envision Neural - Shared JavaScript Functionality

// Page Navigation
const navigation = {
    pages: {
        home: 'index.html',
        demo: 'contact-demo.html', 
        waitlist: 'join-waitlist.html'
    },
    
    navigateTo(page) {
        if (this.pages[page]) {
            window.location.href = this.pages[page];
        }
    }
};

// Form Handling
class FormHandler {
    constructor() {
        this.initializeForms();
    }
    
    initializeForms() {
        // Handle demo form submission
        const demoForm = document.querySelector('#demo-form');
        if (demoForm) {
            demoForm.addEventListener('submit', (e) => this.handleDemoSubmission(e));
        }
        
        // Handle waitlist form submission
        const waitlistForm = document.querySelector('#waitlist-form');
        if (waitlistForm) {
            waitlistForm.addEventListener('submit', (e) => this.handleWaitlistSubmission(e));
        }
        
        // Add form validation
        this.addFormValidation();
    }
    
    handleDemoSubmission(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData.entries());
        
        // Basic validation
        if (!this.validateDemoForm(data)) {
            return;
        }
        
        // Show loading state
        this.showLoadingState(e.target);
        
        // Simulate API call (replace with actual endpoint)
        this.submitDemoRequest(data)
            .then(() => {
                this.showSuccessMessage('demo');
                this.trackEvent('demo_request_submitted', data);
            })
            .catch(() => {
                this.showErrorMessage('demo');
            })
            .finally(() => {
                this.hideLoadingState(e.target);
            });
    }
    
    handleWaitlistSubmission(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData.entries());
        
        // Basic validation
        if (!this.validateWaitlistForm(data)) {
            return;
        }
        
        // Show loading state
        this.showLoadingState(e.target);
        
        // Simulate API call (replace with actual endpoint)
        this.submitWaitlistRequest(data)
            .then(() => {
                this.showSuccessMessage('waitlist');
                this.trackEvent('waitlist_signup', data);
            })
            .catch(() => {
                this.showErrorMessage('waitlist');
            })
            .finally(() => {
                this.hideLoadingState(e.target);
            });
    }
    
    validateDemoForm(data) {
        const required = ['firstName', 'lastName', 'email', 'company', 'jobTitle'];
        const missing = required.filter(field => !data[field] || data[field].trim() === '');
        
        if (missing.length > 0) {
            this.showValidationError(`Please fill in: ${missing.join(', ')}`);
            return false;
        }
        
        if (!this.isValidEmail(data.email)) {
            this.showValidationError('Please enter a valid email address');
            return false;
        }
        
        return true;
    }
    
    validateWaitlistForm(data) {
        const required = ['firstName', 'lastName', 'email', 'company', 'jobTitle'];
        const missing = required.filter(field => !data[field] || data[field].trim() === '');
        
        if (missing.length > 0) {
            this.showValidationError(`Please fill in: ${missing.join(', ')}`);
            return false;
        }
        
        if (!this.isValidEmail(data.email)) {
            this.showValidationError('Please enter a valid email address');
            return false;
        }
        
        return true;
    }
    
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    async submitDemoRequest(data) {
        // Replace with your actual API endpoint
        const response = await fetch('/api/demo-request', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error('Failed to submit demo request');
        }
        
        return response.json();
    }
    
    async submitWaitlistRequest(data) {
        // Replace with your actual API endpoint
        const response = await fetch('/api/waitlist', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error('Failed to submit waitlist request');
        }
        
        return response.json();
    }
    
    showLoadingState(form) {
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Submitting...';
        submitBtn.disabled = true;
        submitBtn.dataset.originalText = originalText;
    }
    
    hideLoadingState(form) {
        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.textContent = submitBtn.dataset.originalText;
        submitBtn.disabled = false;
    }
    
    showSuccessMessage(type) {
        const messages = {
            demo: 'Thank you! We\'ll contact you within 24 hours to schedule your demo.',
            waitlist: 'Welcome to the waitlist! You\'ll receive updates as we get closer to launch.'
        };
        
        this.showNotification(messages[type], 'success');
    }
    
    showErrorMessage(type) {
        const message = 'Something went wrong. Please try again or contact us directly.';
        this.showNotification(message, 'error');
    }
    
    showValidationError(message) {
        this.showNotification(message, 'error');
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 max-w-md transition-all duration-300 transform translate-x-full`;
        
        // Style based on type
        const styles = {
            success: 'bg-green-600 text-white',
            error: 'bg-red-600 text-white', 
            info: 'bg-blue-600 text-white'
        };
        
        notification.className += ` ${styles[type]}`;
        notification.textContent = message;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.classList.remove('translate-x-full');
        }, 100);
        
        // Remove after 5 seconds
        setTimeout(() => {
            notification.classList.add('translate-x-full');
            setTimeout(() => {
                if (notification.parentNode) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 5000);
    }
    
    addFormValidation() {
        // Real-time email validation
        const emailInputs = document.querySelectorAll('input[type="email"]');
        emailInputs.forEach(input => {
            input.addEventListener('blur', () => {
                if (input.value && !this.isValidEmail(input.value)) {
                    input.classList.add('border-red-500');
                    input.classList.remove('border-gray-600');
                } else {
                    input.classList.remove('border-red-500');
                    input.classList.add('border-gray-600');
                }
            });
        });
    }
    
    trackEvent(eventName, data) {
        // Add your analytics tracking here
        // Example: Google Analytics, Mixpanel, etc.
        console.log('Event tracked:', eventName, data);
        
        // Example Google Analytics tracking:
        // if (typeof gtag !== 'undefined') {
        //     gtag('event', eventName, {
        //         'custom_parameters': data
        //     });
        // }
    }
}

// Smooth Scrolling for anchor links
class SmoothScroll {
    constructor() {
        this.initializeSmoothScroll();
    }
    
    initializeSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }
}

// Button click handlers
function setupButtonHandlers() {
    // Contact for Demo buttons
    document.querySelectorAll('[data-action="contact-demo"]').forEach(btn => {
        btn.addEventListener('click', () => navigation.navigateTo('demo'));
    });
    
    // Join Waitlist buttons  
    document.querySelectorAll('[data-action="join-waitlist"]').forEach(btn => {
        btn.addEventListener('click', () => navigation.navigateTo('waitlist'));
    });
    
    // Back to home buttons
    document.querySelectorAll('[data-action="home"]').forEach(btn => {
        btn.addEventListener('click', () => navigation.navigateTo('home'));
    });
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new FormHandler();
    new SmoothScroll();
    setupButtonHandlers();
    
    console.log('Envision Neural website loaded successfully');
});

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { FormHandler, SmoothScroll, navigation };
}