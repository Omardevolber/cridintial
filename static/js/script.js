document.addEventListener('DOMContentLoaded', function() {
    // Handle form submission and loading state
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function() {
            const submitBtn = document.getElementById('submitBtn');
            const buttonText = submitBtn.querySelector('.button-text');
            const spinner = submitBtn.querySelector('.spinner-border');
            
            submitBtn.disabled = true;
            buttonText.textContent = 'جاري التحميل...';
            spinner.classList.remove('d-none');
        });
    }

    // Handle copy buttons in results page
    const copyButtons = document.querySelectorAll('.copy-btn');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const value = this.getAttribute('data-value');
            navigator.clipboard.writeText(value).then(() => {
                const originalText = this.textContent;
                this.textContent = 'تم النسخ!';
                this.classList.add('btn-success');
                
                setTimeout(() => {
                    this.textContent = originalText;
                    this.classList.remove('btn-success');
                }, 2000);
            });
        });
    });
});
