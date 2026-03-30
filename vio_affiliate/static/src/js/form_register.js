/**
 * Form Register JavaScript
 * Handles validation and submission for registration form
 */

(function() {
    'use strict';

    // DOM Elements
    var phoneInput = document.getElementById('phone');
    var phonePrefixDisplay = document.getElementById('phonePrefixDisplay');
    var phonePreview = document.getElementById('phonePreview');
    var form = document.querySelector('.oe_website_form');
    var progressBar = document.getElementById('formProgress');
    var progressText = document.getElementById('progressText');
    var errorAlert = document.getElementById('formErrorAlert');
    var successAlert = document.getElementById('formSuccessAlert');
    var submitBtn = document.getElementById('submitBtn');

    // Required fields for validation
    var requiredFields = [
        { id: 'nama', name: 'Nama Lengkap', type: 'text' },
        { id: 'email', name: 'Email', type: 'email' },
        { id: 'phone', name: 'Nomor Telepon', type: 'phone' },
        { id: 'race', name: 'Sumber Info', type: 'text' },
        { id: 'domisili_id', name: 'Domisili', type: 'select' },
        { id: 'checkaccterm', name: 'Persetujuan Kebijakan', type: 'checkbox' }
    ];

    /**
     * Fungsi untuk menambahkan prefix 62 ke nomor telepon
     * @param {string} value - Nilai input nomor telepon
     * @returns {string} - Nomor telepon dengan prefix 62
     */
    function addPrefix62(value) {
        if (!value || value.trim() === '') {
            return '';
        }

        var cleaned = value.replace(/\D/g, '');

        if (cleaned.startsWith('62')) {
            return cleaned;
        }

        if (cleaned.startsWith('0')) {
            return '62' + cleaned.substring(1);
        }

        return '62' + cleaned;
    }

    /**
     * Format nomor telepon untuk tampilan
     * @param {string} value - Nomor telepon
     * @returns {string} - Nomor telepon yang diformat
     */
    function formatPhoneNumber(value) {
        if (!value || value.trim() === '') {
            return '';
        }

        var cleaned = value.replace(/\D/g, '');

        if (cleaned.length <= 3) {
            return cleaned;
        } else if (cleaned.length <= 7) {
            return cleaned.slice(0, 3) + '-' + cleaned.slice(3);
        } else {
            return cleaned.slice(0, 3) + '-' + cleaned.slice(3, 7) + '-' + cleaned.slice(7, 11);
        }
    }

    /**
     * Validasi email
     * @param {string} email - Email yang akan divalidasi
     * @returns {boolean} - True jika valid
     */
    function isValidEmail(email) {
        var re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    /**
     * Validasi nomor telepon
     * @param {string} phone - Nomor telepon yang akan divalidasi
     * @returns {boolean} - True jika valid
     */
    function isValidPhone(phone) {
        var cleaned = phone.replace(/\D/g, '');
        return cleaned.length >= 9 && cleaned.length <= 14;
    }

    /**
     * Tampilkan pesan error pada field
     * @param {HTMLElement} field - Element field
     * @param {string} message - Pesan error
     */
    function showError(field, message) {
        field.classList.add('is-invalid');
        field.classList.remove('is-valid');
        var errorElement = document.getElementById(field.id + 'Error');
        if (errorElement) {
            errorElement.textContent = message;
        }
    }

    /**
     * Hapus pesan error pada field
     * @param {HTMLElement} field - Element field
     */
    function clearError(field) {
        field.classList.remove('is-invalid');
        var errorElement = document.getElementById(field.id + 'Error');
        if (errorElement) {
            errorElement.textContent = '';
        }
    }

    /**
     * Tampilkan status valid pada field
     * @param {HTMLElement} field - Element field
     */
    function showValid(field) {
        field.classList.add('is-valid');
        field.classList.remove('is-invalid');
    }

    /**
     * Update progress bar
     */
    function updateProgress() {
        var filled = 0;
        var total = requiredFields.length;

        requiredFields.forEach(function(field) {
            var element = document.getElementById(field.id);
            if (element) {
                if (field.type === 'checkbox') {
                    if (element.checked) filled++;
                } else if (field.type === 'select') {
                    if (element.value) filled++;
                } else {
                    if (element.value && element.value.trim() !== '') filled++;
                }
            }
        });

        var percentage = Math.round((filled / total) * 100);
        progressBar.style.width = percentage + '%';
        progressText.textContent = percentage + '% Selesai';

        if (percentage === 100) {
            progressText.textContent = 'Siap dikirim!';
            submitBtn.disabled = false;
        } else {
            submitBtn.disabled = false; // Allow submission with validation
        }
    }

    /**
     * Validasi field secara real-time
     * @param {HTMLElement} field - Element field
     * @param {Object} fieldConfig - Konfigurasi field
     */
    function validateField(field, fieldConfig) {
        var value = field.value ? field.value.trim() : '';

        if (fieldConfig.type === 'checkbox') {
            if (!field.checked) {
                showError(field, 'Anda harus menyetujui kebijakan kami');
                return false;
            }
        } else {
            if (!value) {
                showError(field, fieldConfig.name + ' wajib diisi');
                return false;
            }

            if (fieldConfig.type === 'email') {
                if (!isValidEmail(value)) {
                    showError(field, 'Format email tidak valid');
                    return false;
                }
            }

            if (fieldConfig.type === 'phone') {
                if (!isValidPhone(value)) {
                    showError(field, 'Nomor telepon harus 9-14 digit');
                    return false;
                }
            }
        }

        clearError(field);
        if (value && fieldConfig.type !== 'checkbox') {
            showValid(field);
        }
        return true;
    }

    /**
     * Setup event listeners untuk validasi
     */
    function setupValidationListeners() {
        requiredFields.forEach(function(fieldConfig) {
            var field = document.getElementById(fieldConfig.id);
            if (field) {
                // Validate on blur
                field.addEventListener('blur', function() {
                    validateField(field, fieldConfig);
                    updateProgress();
                });

                // Validate on input (for real-time feedback)
                field.addEventListener('input', function() {
                    if (fieldConfig.type !== 'checkbox') {
                        if (field.value && field.value.trim() !== '') {
                            validateField(field, fieldConfig);
                        } else {
                            clearError(field);
                        }
                        updateProgress();
                    }
                });

                // Validate on change (for checkboxes and selects)
                field.addEventListener('change', function() {
                    validateField(field, fieldConfig);
                    updateProgress();
                });
            }
        });
    }

    /**
     * Validasi seluruh form
     * @returns {boolean} - True jika form valid
     */
    function validateForm() {
        var isValid = true;
        errorAlert.classList.add('d-none');

        requiredFields.forEach(function(fieldConfig) {
            var field = document.getElementById(fieldConfig.id);
            if (field) {
                if (!validateField(field, fieldConfig)) {
                    isValid = false;
                }
            }
        });

        if (!isValid) {
            errorAlert.classList.remove('d-none');
            // Scroll to first error
            var firstError = document.querySelector('.is-invalid');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstError.focus();
            }
        }

        return isValid;
    }

    /**
     * Event handler saat user mengetik di field phone
     */
    phoneInput.addEventListener('input', function(e) {
        var currentValue = e.target.value;

        if (currentValue && currentValue.trim() !== '') {
            var cleaned = currentValue.replace(/\D/g, '');
            e.target.value = cleaned;

            // Update preview
            var formatted = formatPhoneNumber(cleaned);
            if (formatted) {
                phonePreview.textContent = 'Preview: 62 ' + formatted;
            } else {
                phonePreview.textContent = '';
            }
        } else {
            phonePreview.textContent = '';
        }
    });

    /**
     * Event handler saat field phone kehilangan fokus
     */
    phoneInput.addEventListener('blur', function(e) {
        var currentValue = e.target.value;

        if (currentValue && currentValue.trim() !== '') {
            var prefixed = addPrefix62(currentValue);
            e.target.value = prefixed;

            // Update preview with full number
            var formatted = formatPhoneNumber(prefixed.substring(2));
            phonePreview.textContent = 'Preview: ' + prefixed;
        }
    });

    /**
     * Event handler saat form disubmit
     */
    if (form) {
        form.addEventListener('submit', function(e) {
            // Validate form before submit
            if (!validateForm()) {
                e.preventDefault();
                return;
            }

            // Ensure phone has prefix 62
            var currentValue = phoneInput.value;
            if (currentValue && currentValue.trim() !== '') {
                var prefixed = addPrefix62(currentValue);
                phoneInput.value = prefixed;
            }

            // Show loading state
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Mengirim...';
        });
    }

    // Initialize
    setupValidationListeners();
    updateProgress();

})();
