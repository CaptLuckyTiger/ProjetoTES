document.addEventListener('DOMContentLoaded', function () {
    var confirmationModal = document.getElementById('confirmationModal');
    confirmationModal.addEventListener('show.bs.modal', function (event) {
        var button = event.relatedTarget;
        var actionUrl = button.getAttribute('data-url');
        var confirmationForm = document.getElementById('confirmationForm');
        confirmationForm.setAttribute('action', actionUrl);
    });
});
