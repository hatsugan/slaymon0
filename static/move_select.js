document.addEventListener('DOMContentLoaded', function () {
    // Elements for move and slay selection
    const moveButtons = document.querySelectorAll('.move-option');      // Buttons for selecting a move
    const confirmButton = document.getElementById('confirm-move-button'); // Button to confirm move selection
    const switchButton = document.getElementById('switch-button');      // Button to switch the active slay
    const slayCards = document.querySelectorAll('.slay-card-mini');     // Slay cards in the team

    // Variables to keep track of selected move and slay
    let selectedMoveIndex = null;   // Index of the selected move
    let selectedSlayIndex = null;   // Index of the selected slay

    // -----------------------------
    // Handle move selection
    // -----------------------------
    moveButtons.forEach(button => {
        button.addEventListener('click', function () {
            // Remove the 'selected' class from all move buttons
            moveButtons.forEach(btn => btn.classList.remove('selected'));

            // Add the 'selected' class to the clicked button
            this.classList.add('selected');

            // Store the index of the selected move
            selectedMoveIndex = this.getAttribute('data-move-index');

            // Enable the confirm button
            confirmButton.disabled = false;
        });
    });

    // -----------------------------
    // Handle slay selection
    // -----------------------------
    slayCards.forEach(card => {
        card.addEventListener('click', function () {
            // Remove the 'selected' class from all slay cards
            slayCards.forEach(c => c.classList.remove('selected'));

            // Add the 'selected' class to the clicked card
            this.classList.add('selected');

            // Store the index of the selected slay
            selectedSlayIndex = this.getAttribute('data-slay-index');

            // Enable the switch button
            switchButton.disabled = false;
        });
    });

    // -----------------------------
    // Confirm move selection
    // -----------------------------
    confirmButton.addEventListener('click', function () {
        if (selectedMoveIndex !== null) {
            // Send the selected move to the server via an AJAX request
            fetch(`/select_move/${selectedMoveIndex}`, { method: 'POST' })
                .then(response => response.text())
                .then(html => {
                    // Update the page with the server response
                    document.open();
                    document.write(html);
                    document.close();
                });
        }
    });

    // -----------------------------
    // Handle slay switch
    // -----------------------------
    switchButton.addEventListener('click', function () {
        if (selectedSlayIndex !== null) {
            // Send the selected slay to the server via an AJAX request
            fetch(`/switch_slay/${selectedSlayIndex}`, { method: 'POST' })
                .then(response => response.text())
                .then(html => {
                    // Update the page with the server response
                    document.open();
                    document.write(html);
                    document.close();
                });
        }
    });
});
