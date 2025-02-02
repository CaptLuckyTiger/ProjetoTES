document.addEventListener('DOMContentLoaded', function() {
    var confirmDeleteModal = document.getElementById('confirmDeleteModal');
    confirmDeleteModal.addEventListener('show.bs.modal', function(event) {
        var button = event.relatedTarget;
        var model = button.getAttribute('data-model');
        var id = button.getAttribute('data-id');

        var form = document.getElementById('deleteForm');
        form.action = `/delete/${model}/${id}/`;
    });
});