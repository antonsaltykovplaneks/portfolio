document.addEventListener('DOMContentLoaded', function () {
    let isSetMode = false;
    const addNewSetButton = document.querySelector('.btn-success.add-new-set');
    const industryFilterForm = document.getElementById('industry-filters');
    const technologyFilterForm = document.getElementById('technology-filters');
    const projectList = document.getElementById('project-list');
    const cancelButton = document.createElement('button');
    const setNameInput = document.createElement('input');
    const saveSetButton = document.createElement('button');
    const selectedProjectsCounter = document.createElement('span');
    let selectedProjects = new Set();

    cancelButton.classList.add('btn', 'btn-secondary');
    cancelButton.textContent = 'Cancel';
    cancelButton.style.display = 'none';

    setNameInput.type = 'text';
    setNameInput.placeholder = 'Enter set name';
    setNameInput.classList.add('form-control', 'mt-2');
    setNameInput.style.maxWidth = '150px';
    setNameInput.style.display = 'none';

    selectedProjectsCounter.style.display = 'none';
    selectedProjectsCounter.classList.add('ml-2', 'selected-projects-counter', 'badge', 'bg-warning', 'p-2', 'rounded');
    selectedProjectsCounter.textContent = 'Selected: 0';

    saveSetButton.classList.add('btn', 'btn-primary', 'mt-2');
    saveSetButton.textContent = 'Save Set';
    saveSetButton.style.display = 'none';

    addNewSetButton.parentNode.insertBefore(cancelButton, addNewSetButton.nextSibling);
    addNewSetButton.parentNode.insertBefore(setNameInput, cancelButton.nextSibling);
    addNewSetButton.parentNode.insertBefore(saveSetButton, setNameInput.nextSibling);
    addNewSetButton.parentNode.insertBefore(selectedProjectsCounter, saveSetButton.nextSibling);

    // Add new set button click handler
    addNewSetButton.addEventListener('click', function () {
        if (!isSetMode) {
            isSetMode = true;
            toggleSetMode(true);
        }
    });

    // Save set button click handler
    saveSetButton.addEventListener('click', function () {
        const setName = setNameInput.value.trim();
        if (setName) {
            isSetMode = false;
            setNameInput.value = '';
            saveProjectSet(setName);
        } else {
            alert('Please enter a name for the project set.');
        }
    });

    // Cancel button click handler
    cancelButton.addEventListener('click', function () {
        isSetMode = false;
        setNameInput.value = '';
        toggleSetMode(false);
        resetSelectedProjects();
    });

    // Toggle between set mode and normal mode
    function toggleSetMode(isEnabled) {
        addNewSetButton.style.display = isEnabled ? 'none' : 'inline-block';
        cancelButton.style.display = isEnabled ? 'inline-block' : 'none';
        setNameInput.style.display = isEnabled ? 'inline-block' : 'none';
        saveSetButton.style.display = isEnabled ? 'inline-block' : 'none';
        selectedProjectsCounter.style.display = isEnabled ? 'inline-block' : 'none';
        disableFilters(isEnabled);
        replaceProjectButtons(isEnabled ? 'add' : 'reset');
        updateSelectedProjectsCounter();
    }

    // Enable/Disable industry and technology filters
    function disableFilters(disable) {
        industryFilterForm.querySelectorAll('input').forEach(input => {
            if (!input.checked) {
                input.style.opacity = '0.5';
                input.disabled = disable;
            } else {
                input.style.opacity = '1';
            }
        });
        technologyFilterForm.querySelectorAll('input').forEach(input => {
            if (!input.checked) {
                input.disabled = disable;
            } else {
                input.style.opacity = '1';
            }
        });
    }

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

    // Replace project buttons based on action (add/remove or reset)
    function replaceProjectButtons(action) {
        const storedProjects = JSON.parse(localStorage.getItem('selectedProjects')) || [];
        selectedProjects = new Set(storedProjects);

        projectList.querySelectorAll('.project-item').forEach(item => {
            const buttonContainer = item.querySelector('.d-flex');
            buttonContainer.innerHTML = '';

            const projectId = item.dataset.projectId;

            if (action === 'add') {
                const addButton = createAddButton(projectId);
                buttonContainer.appendChild(addButton);
            } else {
                const editButton = createEditButton();
                const deleteButton = createDeleteButton();

                buttonContainer.appendChild(editButton);
                buttonContainer.appendChild(deleteButton);
            }
        });
    }

    // Create Add/Remove button for a project
    function createAddButton(projectId) {
        const addButton = document.createElement('button');
        addButton.classList.add('btn');
        addButton.style.backgroundColor = 'blue';
        addButton.style.color = 'white';
        addButton.textContent = 'Add to set';

        if (selectedProjects.has(projectId)) {
            addButton.textContent = 'Remove from set';
            addButton.style.backgroundColor = 'red';
        }

        addButton.addEventListener('click', function () {
            if (selectedProjects.has(projectId)) {
                selectedProjects.delete(projectId);
                addButton.textContent = 'Add to set';
                addButton.style.backgroundColor = 'blue';
            } else {
                selectedProjects.add(projectId);
                addButton.textContent = 'Remove from set';
                addButton.style.backgroundColor = 'red';
            }
            localStorage.setItem('selectedProjects', JSON.stringify(Array.from(selectedProjects)));
            updateSelectedProjectsCounter();
        });

        return addButton;
    }

    // Create Edit button for a project
    function createEditButton() {
        const editButton = document.createElement('a');
        editButton.classList.add('btn', 'btn-link');
        editButton.textContent = 'Edit';
        return editButton;
    }

    // Create Delete button for a project
    function createDeleteButton() {
        const deleteButton = document.createElement('a');
        deleteButton.classList.add('btn', 'btn-link', 'text-danger');
        deleteButton.textContent = 'Delete';
        return deleteButton;
    }

    // Reset selected projects
    function resetSelectedProjects() {
        selectedProjects.clear();
        localStorage.removeItem('selectedProjects');
        toggleSetMode(false);
        updateSelectedProjectsCounter();
    }

    // Update the selected projects counter
    function updateSelectedProjectsCounter() {
        selectedProjectsCounter.textContent = `Selected: ${selectedProjects.size}`;
    }

    // Save project set to server
    function saveProjectSet(title) {
        const projectIds = Array.from(selectedProjects);

        fetch('/sets/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify({
                title: title,
                projects: projectIds
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('Project set saved successfully!');
                    resetSelectedProjects();
                } else {
                    alert('Failed to save project set: ' + data.message);
                }
            })
            .catch(error => console.error('Error:', error));
    }

    document.addEventListener('DOMContentLoaded', function () {
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
                                // remove the project set from the DOM
                                this.closest('.project-item').remove();
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
    });

    const debounce = (func, delay) => {
        let timeoutId;
        return function (...args) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(this, args), delay);
        };
    };

    const updateURLParams = () => {
        const searchQuery = document.getElementById('project-search').value.trim();
        const industries = Array.from(document.querySelectorAll('.industry-filter:checked'))
            .map(el => el.value)
            .filter(value => value);
        const technologies = Array.from(document.querySelectorAll('.technology-filter:checked'))
            .map(el => el.value)
            .filter(value => value);

        const urlParams = new URLSearchParams(window.location.search);

        if (searchQuery) {
            urlParams.set('q', searchQuery);
        } else {
            urlParams.delete('q');
        }

        urlParams.delete('industry');
        industries.forEach(ind => urlParams.append('industry', ind));

        urlParams.delete('technology');
        technologies.forEach(tech => urlParams.append('technology', tech));

        window.history.replaceState({}, '', `${window.location.pathname}?${urlParams.toString()}`);

        fetchProjects();
    };

    const fetchProjects = (page = null) => {
        const urlParams = new URLSearchParams(window.location.search);
        if (page) {
            urlParams.set('page', page);
        }

        fetch(`${window.location.pathname}?${urlParams.toString()}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => response.text())
            .then(data => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(data, 'text/html');

                // Update the project list
                const newProjectList = doc.getElementById('project-list').innerHTML;
                document.getElementById('project-list').innerHTML = newProjectList;

                // Update the industry facets
                const newIndustryFilters = doc.getElementById('industry-filters').innerHTML;
                document.getElementById('industry-filters').innerHTML = newIndustryFilters;

                // Update the technology facets
                const newTechnologyFilters = doc.getElementById('technology-filters').innerHTML;
                document.getElementById('technology-filters').innerHTML = newTechnologyFilters;

                // Update the pagination links
                const newPagination = doc.querySelector('.pagination').outerHTML;
                document.querySelector('.pagination').outerHTML = newPagination;

                if (isSetMode == true) {
                    replaceProjectButtons('add');
                    disableFilters(true);
                }
                bindEventListeners();
            })
            .catch(error => {
                console.error('Error fetching projects:', error);
            });
    };

    const bindEventListeners = () => {
        document.querySelectorAll('.industry-filter').forEach(el => {
            el.addEventListener('change', updateURLParams);
        });

        document.querySelectorAll('.technology-filter').forEach(el => {
            el.addEventListener('change', updateURLParams);
        });

        document.querySelectorAll('.page-link').forEach(link => {
            link.addEventListener('click', function (event) {
                event.preventDefault();
                const page = new URL(link.href).searchParams.get('page');
                fetchProjects(page);
            });
        });

        document.querySelectorAll('.industry-link').forEach(link => {
            link.addEventListener('click', function (event) {
                event.preventDefault();
                const industry = this.getAttribute('data-industry');
                const industryCheckbox = document.querySelector(`.industry-filter[value="${industry}"]`);
                if (industryCheckbox.checked) {
                    industryCheckbox.checked = false;
                } else {
                    if (industryCheckbox.disabled) {
                        return;
                    }
                    industryCheckbox.checked = true;
                }
                updateURLParams();
            });
        });

        document.querySelectorAll('.technology-link').forEach(link => {
            link.addEventListener('click', function (event) {
                event.preventDefault();
                const technology = this.getAttribute('data-technology');
                const technologyCheckbox = document.querySelector(`.technology-filter[value="${technology}"]`);
                if (technologyCheckbox.checked) {
                    technologyCheckbox.checked = false;
                } else {
                    if (technologyCheckbox.disabled) {
                        return;
                    }
                    technologyCheckbox.checked = true;
                }
                updateURLParams();
            });
        });
    };

    const debouncedFetch = debounce(updateURLParams, 300);

    document.getElementById('project-search').addEventListener('input', debouncedFetch);

    bindEventListeners();

    const industrySearch = document.getElementById('industry-search');
    const technologySearch = document.getElementById('technology-search');

    industrySearch.addEventListener('input', function () {
        const query = industrySearch.value.toLowerCase();
        filterCheckboxes('industry-filter', query);
    });

    technologySearch.addEventListener('input', function () {
        const query = technologySearch.value.toLowerCase();
        filterCheckboxes('technology-filter', query);
    });

    function filterCheckboxes(filterClass, query) {
        const checkboxes = document.querySelectorAll(`.${filterClass}`);
        checkboxes.forEach(checkbox => {
            const label = checkbox.nextElementSibling;
            const text = label.textContent.toLowerCase();
            if (text.includes(query)) {
                checkbox.parentElement.style.display = '';
            } else {
                checkbox.parentElement.style.display = 'none';
            }
        });
    }

    document.querySelectorAll('.delete-project').forEach(button => {
        button.addEventListener('click', function () {
            const projectId = this.getAttribute('data-project-id');
            let text = 'Are you sure you want to delete this project?';
            if (confirm(text)) {
                fetch(`/projects/${projectId}/`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    }
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            document.querySelector(`.project-item[data-project-id="${projectId}"]`).remove();
                        }
                    })
                    .catch(error => console.error('Error:', error));
            }
        });
    });

    const addProjectForm = document.getElementById('addProjectForm');

    addProjectForm.addEventListener('submit', function (event) {
        event.preventDefault();

        const title = document.getElementById('projectTitle').value;
        const industries = document.getElementById('projectIndustries').value.split(',').map(item => item.trim());
        const description = document.getElementById('projectDescription').value;
        const technologies = document.getElementById('projectTechnologies').value.split(',').map(item => item.trim());
        const url = document.getElementById('projectUrl').value;

        const projectData = {
            title: title,
            industries: industries,
            description: description,
            technologies: technologies,
            url: url
        };

        fetch('/projects/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(projectData)
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('Project added successfully!');
                    addProjectForm.reset();
                } else {
                    alert('Failed to add project: ' + data.message);
                }
            })
            .catch(error => console.error('Error:', error));
    });
});