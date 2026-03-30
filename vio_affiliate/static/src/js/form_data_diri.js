/**
 * Form Data Diri JavaScript
 * Handles validation and submission for personal data form
 */

(function() {
    'use strict';

    /**
     * Validate individual form field
     * @param {HTMLElement} field - The form field to validate
     * @returns {boolean} - True if field is valid
     */
    function validateField(field) {
        const formGroup = field.closest('.form-group');
        const errorFeedback = formGroup.querySelector('.invalid-feedback');
        const validFeedback = formGroup.querySelector('.valid-feedback');
        const isRequired = field.hasAttribute('required');
        const value = field.value.trim();
        let isValid = true;

        // Remove previous validation classes
        field.classList.remove('is-valid', 'is-invalid');

        // Check if field is required and empty
        if (isRequired && value === '') {
            isValid = false;
        }

        // Validate specific field types
        if (value !== '') {
            // Email validation
            if (field.type === 'email') {
                const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                isValid = emailPattern.test(value);
            }

            // Phone validation
            if (field.id === 'input_phone') {
                const phonePattern = /^[0-9]{10,15}$/;
                isValid = phonePattern.test(value);
            }

            // NIK validation
            if (field.id === 'input_nik') {
                const nikPattern = /^[0-9]{16}$/;
                isValid = nikPattern.test(value);
            }

            // Account number validation
            if (field.id === 'input_no_rek') {
                const rekPattern = /^[0-9]{8,20}$/;
                isValid = rekPattern.test(value);
            }

            // URL validation for social media
            if (field.type === 'url' && value !== '') {
                try {
                    new URL(value);
                } catch (err) {
                    isValid = false;
                }
            }
        }

        // Apply validation classes
        if (isValid && value !== '') {
            field.classList.add('is-valid');
        } else if (value !== '') {
            field.classList.add('is-invalid');
        }

        return isValid;
    }

    /**
     * Initialize form validation and submission handlers
     */
    function initFormValidation() {
        const form = document.getElementById('formDataDiri');

        if (!form) {
            return;
        }

        const submitBtn = document.getElementById('submitBtn');
        const successMessage = document.getElementById('successMessage');

        // Form submission handler
        form.addEventListener('submit', function(e) {
            const fields = form.querySelectorAll('input[required]');
            let isFormValid = true;

            // Validate all required fields
            fields.forEach(function(field) {
                if (!validateField(field) || field.value.trim() === '') {
                    isFormValid = false;
                    field.classList.add('is-invalid');
                }
            });

            // Prevent submission if form is invalid
            if (!isFormValid) {
                e.preventDefault();

                // Scroll to first invalid field
                const firstInvalid = form.querySelector('.is-invalid');
                if (firstInvalid) {
                    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    firstInvalid.focus();
                }
                return;
            }

            // Show loading state
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;

            // Simulate form submission (remove this in production)
            setTimeout(function() {
                submitBtn.classList.remove('loading');
                submitBtn.disabled = false;
                successMessage.classList.add('show');

                // Scroll to success message
                successMessage.scrollIntoView({ behavior: 'smooth', block: 'start' });

                // Hide success message after 5 seconds
                setTimeout(function() {
                    successMessage.classList.remove('show');
                }, 5000);
            }, 1500);
        });

        // Real-time validation on blur
        document.querySelectorAll('.form-control').forEach(function(field) {
            field.addEventListener('blur', function() {
                validateField(this);
            });
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initFormValidation);
    } else {
        initFormValidation();
    }

})();
