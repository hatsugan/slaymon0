// move_select.js
document.addEventListener('DOMContentLoaded', function () {
    const moveButtons = document.querySelectorAll('.move-option');

    moveButtons.forEach(button => {
        button.addEventListener('click', function () {
            moveButtons.forEach(btn => btn.classList.remove('selected'));
            this.classList.add('selected');

            const moveIndex = this.getAttribute('data-move-index');

            // Send the selected move to the server via an AJAX request
            fetch(`/select_move/${moveIndex}`, { method: 'POST' })
                .then(response => response.text())
                .then(html => {
                    document.open();
                    document.write(html);
                    document.close();
                });
        });
    });
});
