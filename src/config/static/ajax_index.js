document.addEventListener('DOMContentLoaded', function () {
    let isSetMode = false;
    const addNewSetButton = document.querySelector('.btn-success.add-new-set');
    const industryFilterForm = document.getElementById('industry-filters');
    const technologyFilterForm = document.getElementById('technology-filters');
    const projectList = document.getElementById('project-list');
    const cancelButton = document.createElement('button');
    let selectedProjects = new Set();

    cancelButton.classList.add('btn', 'btn-secondary');
    cancelButton.textContent = 'Cancel';
    cancelButton.style.display = 'none';

    addNewSetButton.parentNode.insertBefore(cancelButton, addNewSetButton.nextSibling);

    addNewSetButton.addEventListener('click', function () {
        if (!isSetMode) {
            isSetMode = true;
            addNewSetButton.textContent = 'Save changes';
            cancelButton.style.display = 'inline-block';
            disableFilters(true);
            replaceProjectButtons('add');
        } else {
            const setName = prompt('Enter the name of your project set:');
            if (setName) {
                saveProjectSet(setName);
            }
        }
    });

    cancelButton.addEventListener('click', function () {
        isSetMode = false;
        addNewSetButton.textContent = 'Add new set';
        cancelButton.style.display = 'none';
        disableFilters(false);
        replaceProjectButtons('reset');
        selectedProjects.clear();
        localStorage.removeItem('selectedProjects');
    });


    function disableFilters(disable) {
        industryFilterForm.style.opacity = disable ? '0.5' : '1';
        industryFilterForm.querySelectorAll('input').forEach(input => {
            input.disabled = disable;
        });
        technologyFilterForm.style.opacity = disable ? '0.5' : '1';
        technologyFilterForm.querySelectorAll('input').forEach(input => {
            input.disabled = disable;
        });
    }

    function replaceProjectButtons(action) {

        const storedProjects = JSON.parse(localStorage.getItem('selectedProjects')) || [];
        selectedProjects = new Set(storedProjects);

        projectList.querySelectorAll('.project-item').forEach(item => {
            const buttonContainer = item.querySelector('.d-flex');
            buttonContainer.innerHTML = '';

            const projectId = item.dataset.projectId;

            if (action === 'add') {
                const addButton = document.createElement('button');
                addButton.classList.add('btn');
                addButton.style.backgroundColor = 'blue';
                addButton.style.color = 'white';
                addButton.textContent = 'Add to set';
                buttonContainer.appendChild(addButton);

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
                });
            } else {
                const editButton = document.createElement('a');
                editButton.classList.add('btn', 'btn-link');
                editButton.textContent = 'Edit';
                buttonContainer.appendChild(editButton);

                const deleteButton = document.createElement('a');
                deleteButton.classList.add('btn', 'btn-link', 'text-danger');
                deleteButton.textContent = 'Delete';
                buttonContainer.appendChild(deleteButton);
            }
        });
    }

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
                } else {
                    alert('Failed to save project set: ' + data.message);
                }
                isSetMode = false;
                addNewSetButton.textContent = 'Add new set';
                cancelButton.style.display = 'none';
                disableFilters(false);
                replaceProjectButtons('reset');
                selectedProjects.clear();
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }
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
});