document.addEventListener('DOMContentLoaded', function() {
    // Configura o modal para todos os botões com data-confirm
    document.querySelectorAll('[data-confirm]').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Configurações do modal
            const message = this.dataset.confirm;
            const formAction = this.dataset.action;
            const formMethod = this.dataset.method || 'post';

            // Atualiza o modal
            document.getElementById('confirmationModalMessage').textContent = message;
            const form = document.getElementById('confirmationForm');
            form.action = formAction;
            form.method = formMethod;

            // Mostra o modal
            new bootstrap.Modal(document.getElementById('confirmationModal')).show();
        });
    });
});