document.addEventListener('DOMContentLoaded', function () {
    const csrfToken = getCookie('csrftoken');

    // Delete project set button click handler
    document.querySelectorAll('.delete-project-set').forEach(button => {
        button.addEventListener('click', function () {
            const projectSetId = this.getAttribute('data-project-set-id');
            if (confirm('Are you sure you want to delete this project set?')) {
                fetch(`/sets/${projectSetId}/`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
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
            const header = this.closest('.card-header');
            const titleElement = header.querySelector('h3');
            const currentTitle = titleElement.textContent;

            if (this.textContent === 'Rename') {
                let inputField = document.querySelector('.input-field-rename')
                if (inputField) {
                    return;
                }
                inputField = document.createElement('input');
                inputField.type = 'text';
                inputField.value = currentTitle;
                inputField.classList.add('form-control');
                inputField.classList.add('input-field-rename');
                inputField.style.width = '80%';

                // Replace the title with the input field
                header.replaceChild(inputField, titleElement);
                inputField.focus();
                this.textContent = 'Save';

                // Save the new title on Enter key press
                inputField.addEventListener('keypress', function (event) {
                    if (event.key === 'Enter') {
                        saveTitle(inputField, titleElement, header, projectSetId, button);
                    }
                });

                button.addEventListener('click', function () {
                    saveTitle(inputField, titleElement, header, projectSetId, button);
                });

                // Revert to the original title if input loses focus without saving
                inputField.addEventListener('blur', function () {
                    if (button.textContent === 'Save') {
                        saveTitle(inputField, titleElement, header, projectSetId, button);
                    }
                });
            }
        });
    });

    function saveTitle(inputField, titleElement, header, projectSetId, button) {
        const newName = inputField.value.trim();
        if (newName) {
            fetch(`/sets/${projectSetId}/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
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
                        // Replace the input field with the new title
                        titleElement.textContent = newName;
                        header.replaceChild(titleElement, inputField);
                        button.textContent = 'Rename';
                        inputField = null;
                    }
                })
                .catch(error => console.error('Error:', error));
        }
    }

    fetchIndustries();
    fetchTechnologies();

    document.querySelectorAll('.edit-project').forEach(button => {
        button.addEventListener('click', function () {
            const projectItem = this.closest('.project-item');
            toggleEditMode(projectItem, true);
        });
    });

    document.querySelectorAll('.edit-form').forEach(form => {
        form.addEventListener('submit', function (event) {
            event.preventDefault();

            const projectItem = this.closest('.project-item');
            const projectId = projectItem.getAttribute('data-project-id');

            const title = projectItem.querySelector('input[name="title"]').value;
            const description = projectItem.querySelector('textarea[name="description"]').value;
            const industries = Array.from(projectItem.querySelector('select[name="industries"]').selectedOptions).map(option => option.value);
            const technologies = Array.from(projectItem.querySelector('select[name="technologies"]').selectedOptions).map(option => option.value);
            const url = projectItem.querySelector('input[name="url"]').value;

            saveProject(projectId, title, description, industries, technologies, url, projectItem);
        });
    });

    function toggleEditMode(projectItem, isEditMode) {
        const fields = ['title', 'description', 'industries', 'technologies', 'url'];
        fields.forEach(field => {
            const spanElement = projectItem.querySelector(`.editable-${field}`);
            if (isEditMode) {
                isOriginalLabel = document.querySelector('small[name="is-original-project"]');
                if (isOriginalLabel) {
                    isOriginalLabel.classList.add('d-none');
                }
                let inputElement;
                if (field === 'description') {
                    inputElement = document.createElement('textarea');
                    inputElement.value = spanElement.textContent.trim();
                } else if (field === 'industries' || field === 'technologies') {
                    inputElement = createMultiSelectField(field, spanElement);
                } else {
                    inputElement = document.createElement('input');
                    inputElement.type = 'text';
                    inputElement.value = spanElement.textContent.trim();
                }
                inputElement.name = field;
                inputElement.classList.add('form-control', 'mb-2');
                spanElement.replaceWith(inputElement);
            } else {
                const inputElement = projectItem.querySelector(`[name="${field}"]`);
                const newSpan = document.createElement('span');
                if (field === 'industries' || field === 'technologies') {
                    newSpan.textContent = Array.from(inputElement.selectedOptions).map(option => option.text).join(', ');
                } else {
                    newSpan.textContent = inputElement.value;
                }
                newSpan.classList.add(`editable-${field}`);
                inputElement.replaceWith(newSpan);
                isOriginalLabel = document.querySelector('small[name="is-original-project"]');
                if (isOriginalLabel) {
                    isOriginalLabel.classList.remove('d-none');
                    isOriginalLabel.text = 'updated';
                }
            }
        });

        projectItem.querySelector('.edit-project').classList.toggle('d-none', isEditMode);
        projectItem.querySelector('.save-project').classList.toggle('d-none', !isEditMode);
    }

    function createMultiSelectField(field, spanElement) {
        const selectElement = document.createElement('select');
        selectElement.name = field;
        selectElement.multiple = true;
        selectElement.classList.add('form-control', 'mb-2');

        const optionsData = field === 'industries' ? industriesOptions : technologiesOptions;

        optionsData.forEach(optionData => {
            const optionElement = document.createElement('option');
            optionElement.value = optionData.id;
            optionElement.text = optionData.title;

            if (spanElement.textContent.includes(optionData.title)) {
                optionElement.selected = true;
            }

            selectElement.appendChild(optionElement);
        });

        return selectElement;
    }

    function saveProject(projectId, title, description, industries, technologies, url, projectItem) {
        fetch(`/projects/${projectId}/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                title: title,
                description: description,
                industries: industries,
                technologies: technologies,
                url: url
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    toggleEditMode(projectItem, false);
                }
            })
            .catch(error => console.error('Error:', error));
    }

    function fetchIndustries() {
        fetch('/industries/')
            .then(response => response.json())
            .then(data => {
                industriesOptions = data;
            })
            .catch(error => console.error('Error fetching industries:', error));
    }

    function fetchTechnologies() {
        fetch('/technologies/')
            .then(response => response.json())
            .then(data => {
                technologiesOptions = data;
            })
            .catch(error => console.error('Error fetching technologies:', error));
    }
    let industriesOptions = [];
    let technologiesOptions = [];
});