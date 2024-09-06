document.addEventListener('DOMContentLoaded', function () {
    // Delete project set button click handler
    document.querySelectorAll('.delete-project-set').forEach(button => {
        button.addEventListener('click', function () {
            const projectSetId = this.getAttribute('data-project-set-id');
            if (confirm('Are you sure you want to delete this project set?')) {
                fetch(`/sets/${projectSetId}/`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            alert('Project set deleted successfully!');
                            // Remove the project set from the DOM
                            this.closest('.card').remove();
                        } else {
                            alert('Failed to delete project set.');
                        }
                    })
                    .catch(error => console.error('Error:', error));
            }
        });
    });

    // Function to get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Toggle SVG icon on collapse
    document.querySelectorAll('.toggle-svg').forEach(button => {
        button.addEventListener('click', function () {
            const svgIcon = document.getElementById(`svg-icon-${this.getAttribute('data-bs-target').split('-').pop()}`);
            if (svgIcon) {
                svgIcon.classList.toggle('rotate-180');
            }
        });
    });
});