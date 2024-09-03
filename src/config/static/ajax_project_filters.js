document.addEventListener('DOMContentLoaded', function () {
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

    const fetchProjects = () => {
        fetch(window.location.href, {
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

                // Rebind the event listeners after updating the filters
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
    };

    const debouncedFetch = debounce(updateURLParams, 300);

    document.getElementById('project-search').addEventListener('input', debouncedFetch);

    bindEventListeners();

    // document.getElementById('industry-search').addEventListener('input', debouncedFetch);
    // document.getElementById('technology-search').addEventListener('input', debouncedFetch);

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
