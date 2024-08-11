document.addEventListener('DOMContentLoaded', function () {
    const moveOptions = document.querySelectorAll('.move-option');
    const traitElements = document.querySelectorAll('.trait');
    const tooltip = document.getElementById('move-tooltip'); // Using the same tooltip div

    function showTooltip(event, content) {
        tooltip.innerHTML = content;

        // Temporarily show the tooltip off-screen to calculate its dimensions
        tooltip.style.left = '-9999px';
        tooltip.style.top = '-9999px';
        tooltip.style.display = 'block';

        const tooltipWidth = tooltip.offsetWidth;
        const tooltipHeight = tooltip.offsetHeight;
        const elementRect = event.target.getBoundingClientRect();

        // Get the current scroll position
        const scrollTop = window.scrollY;
        const scrollLeft = window.scrollX;

        // Now move the tooltip to the correct position
    tooltip.style.left = `${scrollLeft + elementRect.left + (elementRect.width / 2) - (tooltipWidth / 2)}px`;
    tooltip.style.top = `${scrollTop + elementRect.top - tooltipHeight - 10}px`; // 10px above the element
    tooltip.style.display = 'block';
    }


    // Traits tooltip logic
    traitElements.forEach(trait => {
        trait.addEventListener('contextmenu', function (event) {
            event.preventDefault();

            const traitData = this.dataset;
            const traitTags = traitData.tags.split(',').map(tag => tag.trim());

            let extraContent = "";
            if (traitTags.includes('Body Modifier')) {
                extraContent = "<p>note: Body Modifier traits add to Slay's current STR, HAR, DUR, SPE</p>";
            } else {
                extraContent = "<p>note: Non-Body-Modifier traits add to Slay's current STR and SPE, but add their HAR and DUR to 0. </p>";
            }

            const content = `
                <h3>${traitData.name}</h3>
                <p><strong>Biomass Cost</strong> ${traitData.cost}</p>
                <p><strong>STR</strong> ${traitData.strength} | <strong>HAR</strong> ${traitData.hardness} | <strong>DUR</strong> ${traitData.durability} | <strong>SPE</strong> ${traitData.speed}</p>
                <p><strong>Tags</strong> ${traitData.tags}</p>
                ${extraContent}
                <p>${traitData.description}</p>
            `;

            showTooltip(event, content);
        });
    });

    // Moves tooltip logic
    moveOptions.forEach(moveOption => {
        moveOption.addEventListener('click', function () {
            moveOptions.forEach(m => m.classList.remove('selected'));
            this.classList.add('selected');
        });

        moveOption.addEventListener('contextmenu', function (event) {
            event.preventDefault();  // Prevent the default context menu from appearing

            const moveData = this.dataset;

            const content = `
                <h3>${moveData.name}</h3>
                <p><strong>POWER</strong> ${moveData.power} | <strong>RECOIL</strong> ${moveData.recoil}</p>
                <p><strong>BLUNT</strong> ${moveData.blunt} | <strong>CUT</strong> ${moveData.cut} | <strong>PIERCE</strong> ${moveData.pierce}</p>
                <p><strong>Uses</strong> ${moveData.trait} <strong>STR</strong> ${moveData.str} | <strong>HAR</strong> ${moveData.har} | <strong>DUR</strong> ${moveData.dur} | <strong>SPE</strong> ${moveData.spe}</p>
                <p>${moveData.description}</p>
            `;

            showTooltip(event, content);
        });
    });

    // Hide the tooltip when clicking anywhere else on the page
    document.addEventListener('click', function () {
        tooltip.style.display = 'none';
    });
});
