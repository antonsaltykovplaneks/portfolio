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
                            // Remove the project set from the DOM
                            this.closest('.card').remove();
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

    // Toggle description
    document.querySelectorAll('.toggle-description').forEach(link => {
        link.addEventListener('click', function (event) {
            event.preventDefault();
            const shortDescription = this.previousElementSibling.previousElementSibling;
            const fullDescription = this.previousElementSibling;
            if (fullDescription.classList.contains('d-none')) {
                shortDescription.classList.add('d-none');
                fullDescription.classList.remove('d-none');
                this.textContent = 'Less';
            } else {
                shortDescription.classList.remove('d-none');
                fullDescription.classList.add('d-none');
                this.textContent = 'More';
            }
        });
    });

    // Update project set
    document.querySelectorAll('.rename-project-set').forEach(button => {
        button.addEventListener('click', function () {
            const projectSetId = this.getAttribute('data-project-set-id');
            const inputField = document.querySelector(`.rename-input[data-project-set-id="${projectSetId}"]`);
            const newName = inputField.value.trim();

            if (inputField.classList.contains('d-none')) {
                inputField.classList.remove('d-none');
                inputField.focus();
            } else if (newName) {
                fetch(`/sets/${projectSetId}/`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        title: newName,
                        projects: Array.from(document.querySelectorAll(`#project-set-${projectSetId} .project-item`)).map(
                            item => {
                                const projectIdElement = item.querySelector('[data-project-id]');
                                const projectId = projectIdElement ? projectIdElement.getAttribute('data-project-id') : null;
                                return projectId;
                            }
                        )
                    })
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            inputField.classList.add('d-none');
                            const header = inputField.closest('.card-header');
                            header.querySelector('h3').textContent = newName;
                        }
                    })
                    .catch(error => console.error('Error:', error));
            }
        });
    });

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
});