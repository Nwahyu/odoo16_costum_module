odoo.define('vio_affiliate.fungsi_2', function(require) {
    "use strict";

    const core = require('web.core');
    const openBtn = document.getElementById('openHowToBtn');
    const closeBtn = document.getElementById('modalFinishBtn');
    const modal = document.getElementById('howToModal');
    const stepDivs = Array.from(modal.querySelectorAll('[data-step]'));
    let currentStep = 1;


        openBtn.addEventListener('click', () => {
            currentStep = 1;
            modal.classList.remove('hidden');
            updateModal();
            document.body.style.overflow = 'hidden';
            requestAnimationFrame(() => {
                modal.classList.remove('opacity-0');
                modal.querySelector('[data-modal-content]').classList.remove('translate-y-5', 'opacity-0');
        });
        });

        closeBtn.addEventListener('click', () => {
            console.log('ainia');
            modal.classList.add('opacity-0');
            modal.querySelector('[data-modal-content]').classList.add('translate-y-5', 'opacity-0');
            setTimeout(() => {
                modal.classList.add('hidden');
            document.body.style.overflow = '';
            }, 300);
        });

        function closeModal() {
            modal.classList.add('opacity-0');
            modal.querySelector('[data-modal-content]').classList.add('translate-y-5', 'opacity-0');
            setTimeout(() => {
                modal.classList.add('hidden');
            document.body.style.overflow = '';
            }, 300);
        }

        function closeHowToModal(e) {
            if (e && e.target === e.currentTarget) closeModal();
            }
        document.addEventListener('keydown', (e) => {
            if (e.key === "Escape" && !modal.classList.contains('hidden')) closeModal();
        });

        document.querySelectorAll('#modalBackBtn, #modalNextBtn').forEach(btn =>
            btn.addEventListener('click', () => {
                if (btn.id === 'modalBackBtn' && currentStep > 1) currentStep--;
                if (btn.id === 'modalNextBtn' && currentStep < stepDivs.length) currentStep++;
                updateModal();
            })
        );
        function updateModal() {
            stepDivs.forEach((div, idx) => div.classList.toggle('active', (idx + 1) === currentStep));
            for (let i = 1; i < stepDivs.length; i++) {
                let sb = document.getElementById('stepbar-' + i);
                if (sb) {
                    if (currentStep > i) {
                        sb.style.backgroundColor = 'rgb(37,99,235)'; // Tailwind text-vio-blue
                    } else if (currentStep === i) {
                        sb.style.backgroundColor = 'rgb(37,99,235)';
                    } else {
                        sb.style.backgroundColor = '#9ca3af'; // Tailwind text-neutral-gray
                    }
                }
            }
            document.getElementById('modalBackBtn').classList.toggle('hidden', currentStep === 1);
            document.getElementById('modalNextBtn').classList.toggle('hidden', currentStep === stepDivs.length);
            document.getElementById('modalFinishBtn').classList.toggle('hidden', currentStep !== stepDivs.length);
        }


});