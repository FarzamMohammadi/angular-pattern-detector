document.addEventListener('DOMContentLoaded', function() {
    // Pattern preview interactions
    const previews = document.querySelectorAll('.preview-container');
    previews.forEach(preview => {
        preview.addEventListener('click', () => {
            preview.classList.toggle('expanded');
        });
    });

    // Code snippet copy functionality
    const codeBlocks = document.querySelectorAll('pre code');
    codeBlocks.forEach(block => {
        const copyButton = document.createElement('button');
        copyButton.textContent = 'Copy';
        copyButton.className = 'copy-button';
        copyButton.addEventListener('click', () => {
            navigator.clipboard.writeText(block.textContent);
            copyButton.textContent = 'Copied!';
            setTimeout(() => {
                copyButton.textContent = 'Copy';
            }, 2000);
        });
        block.parentNode.insertBefore(copyButton, block);
    });

    // Interactive form handling
    const forms = document.querySelectorAll('.pattern-form form');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            alert('Form submitted!');
        });
    });

    // List item interactions
    const listItems = document.querySelectorAll('.pattern-list li');
    listItems.forEach(item => {
        item.addEventListener('click', () => {
            item.classList.toggle('selected');
        });
    });

    // Add pattern comparison functionality
    initializePatternComparison();
});

function initializePatternComparison() {
    const compareButtons = document.querySelectorAll('.compare-button');
    const comparisonModal = document.getElementById('comparison-modal');
    const selectedPatterns = new Set();

    compareButtons.forEach(button => {
        button.addEventListener('click', () => {
            const patternId = button.dataset.patternId;
            if (selectedPatterns.has(patternId)) {
                selectedPatterns.delete(patternId);
                button.classList.remove('selected');
            } else if (selectedPatterns.size < 2) {
                selectedPatterns.add(patternId);
                button.classList.add('selected');
            }

            if (selectedPatterns.size === 2) {
                showComparison([...selectedPatterns]);
            }
        });
    });

    function showComparison(patterns) {
        // Fetch and display comparison data
        fetch(`/api/compare-patterns?p1=${patterns[0]}&p2=${patterns[1]}`)
            .then(response => response.json())
            .then(data => {
                renderComparison(data);
                comparisonModal.classList.add('active');
            });
    }
}