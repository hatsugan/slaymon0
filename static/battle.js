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

// TOOLTIP
document.addEventListener('DOMContentLoaded', function () {
    const moveOptions = document.querySelectorAll('.move-option');
    const tooltip = document.getElementById('move-tooltip');
    const selectedMoveInput = document.getElementById('selected_move_input');

    moveOptions.forEach(moveOption => {
        moveOption.addEventListener('click', function () {
            // Remove the selected class from all moves
            moveOptions.forEach(m => m.classList.remove('selected'));

            // Add the selected class to the clicked move
            this.classList.add('selected');

            // Update the hidden input with the selected move
            selectedMoveInput.value = this.dataset.longName;
        });

        moveOption.addEventListener('contextmenu', function (event) {
            event.preventDefault();  // Prevent the default context menu from appearing

            const moveData = this.dataset;

            tooltip.innerHTML = `
                <h3>${moveData.name}</h3>
                <p><strong>POWER</strong>: ${moveData.power} | <strong>RECOIL</strong>: ${moveData.recoil} | <strong>BLUNT</strong>: ${moveData.blunt} | <strong>CUT</strong>: ${moveData.cut} | <strong>PIERCE</strong>: ${moveData.pierce}</p>
                <p><strong>Uses</strong> ${moveData.trait} <strong>STR</strong>: ${moveData.str} | <strong>HAR</strong>: ${moveData.har} | <strong>DUR</strong>: ${moveData.dur} | <strong>SPE</strong>: ${moveData.spe}</p>
                <p>${moveData.description}</p>
            `;
            tooltip.style.left = `${event.pageX + 10}px`;
            tooltip.style.top = `${event.pageY + 10}px`;
            tooltip.style.display = 'block';
        });

        // Hide the tooltip when clicking anywhere else on the page
        document.addEventListener('click', function () {
            tooltip.style.display = 'none';
        });
    });
});

