document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.show-description').forEach(button => {
        button.addEventListener('click', function () {
            const projectId = button.getAttribute('data-project-id');
            const moreText = button.previousElementSibling;

            if (button.getAttribute('data-state') === 'hidden') {
                // Show the full description
                moreText.style.display = 'inline';
                button.textContent = 'Hide';
                button.setAttribute('data-state', 'visible');
            } else {
                // Hide the full description
                moreText.style.display = 'none';
                button.textContent = 'Show';
                button.setAttribute('data-state', 'hidden');
            }
        });
    });
});
