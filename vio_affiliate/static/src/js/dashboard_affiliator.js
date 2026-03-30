/**
 * Dashboard Affiliator JavaScript
 * Handles dashboard interactions and copy functionality
 */

(function() {
    'use strict';

    /**
     * Copy Referral Code Function
     * Copies the referral code to clipboard and updates UI
     */
    function copyReferralCode() {
        const code = document.getElementById('referralCode').innerText;
        navigator.clipboard.writeText(code).then(function() {
            const copyIcon = document.getElementById('copyIcon');
            const copyText = document.getElementById('copyText');

            copyIcon.className = 'fas fa-check copy-success';
            copyText.textContent = 'Berhasil Disalin!';

            setTimeout(function() {
                copyIcon.className = 'fas fa-copy';
                copyText.textContent = 'Salin Kode';
            }, 2000);
        }).catch(function(err) {
            console.error('Gagal menyalin: ', err);
            alert('Gagal menyalin kode. Silakan coba lagi.');
        });
    }

    /**
     * Copy Affiliate Link Function
     * Copies the affiliate link to clipboard and updates UI
     */
    function copyAffiliateLink(event) {
        const link = document.getElementById('affiliateLink').value;
        navigator.clipboard.writeText(link).then(function() {
            // Handle case when event is not provided
            let btn;
            if (event && event.target) {
                btn = event.target.closest('button');
            } else {
                // Find the button next to the affiliate link input
                const inputElement = document.getElementById('affiliateLink');
                btn = inputElement.nextElementSibling;
            }

            if (btn) {
                const originalHTML = btn.innerHTML;

                btn.innerHTML = '<i class="fas fa-check"></i>';
                btn.classList.add('bg-success');
                btn.classList.remove('bg-primary-blue');

                setTimeout(function() {
                    btn.innerHTML = originalHTML;
                    btn.classList.remove('bg-success');
                    btn.classList.add('bg-primary-blue');
                }, 2000);
            }
        }).catch(function(err) {
            console.error('Gagal menyalin: ', err);
            alert('Gagal menyalin link. Silakan coba lagi.');
        });
    }

    /**
     * Initialize tooltips
     */
    function initTooltips() {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    /**
     * Initialize dashboard functionality
     */
    function initDashboard() {
        // Make functions globally accessible for onclick handlers
        window.copyReferralCode = copyReferralCode;
        window.copyAffiliateLink = copyAffiliateLink;

        // Initialize tooltips when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initTooltips);
        } else {
            initTooltips();
        }
    }

    // Initialize dashboard
    initDashboard();

})();
