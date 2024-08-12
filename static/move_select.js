// move_select.js
document.addEventListener('DOMContentLoaded', function () {
    const moveButtons = document.querySelectorAll('.move-option');
    const confirmButton = document.getElementById('confirm-move-button');
    let selectedMoveIndex = null;

    moveButtons.forEach(button => {
        button.addEventListener('click', function () {
            moveButtons.forEach(btn => btn.classList.remove('selected'));
            this.classList.add('selected');

            selectedMoveIndex = this.getAttribute('data-move-index');

            // Enable the confirm button
            confirmButton.disabled = false;
        });
    });

    confirmButton.addEventListener('click', function () {
        if (selectedMoveIndex !== null) {
            // Send the selected move to the server via an AJAX request
            fetch(`/select_move/${selectedMoveIndex}`, { method: 'POST' })
                .then(response => response.text())
                .then(html => {
                    document.open();
                    document.write(html);
                    document.close();
                });
        }
    });
});
