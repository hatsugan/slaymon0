// MOVE SELECT
document.addEventListener('DOMContentLoaded', function () {
    const moveButtons = document.querySelectorAll('.move-option');
    const selectedMoveInput = document.getElementById('selected_move_input');

    moveButtons.forEach(button => {
        button.addEventListener('click', function () {
            // Remove the 'selected' class from all buttons
            moveButtons.forEach(btn => btn.classList.remove('selected'));

            // Add the 'selected' class to the clicked button
            this.classList.add('selected');

            // Set the hidden input's value to the selected move's data-move value
            selectedMoveInput.value = this.getAttribute('data-move');
        });
    });
});


