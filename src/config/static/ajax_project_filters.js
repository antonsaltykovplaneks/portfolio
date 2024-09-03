document.addEventListener('DOMContentLoaded', function () {
    const debounce = (func, delay) => {
        let timeoutId;
        return function (...args) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(this, args), delay);
        };
    };

    const fetchProjects = () => {
        const searchQuery = document.getElementById('project-search').value.trim();
        const industries = Array.from(document.querySelectorAll('.industry-filter:checked'))
            .map(el => el.value)
            .filter(value => value); // Remove empty strings
        const technologies = Array.from(document.querySelectorAll('.technology-filter:checked'))
            .map(el => el.value)
            .filter(value => value); // Remove empty strings

        const urlParams = new URLSearchParams();

        if (searchQuery) {
            urlParams.append('q', searchQuery);
        }

        industries.forEach(ind => urlParams.append('industry', ind));
        technologies.forEach(tech => urlParams.append('technology', tech));

        fetch(`?${urlParams.toString()}`, {
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
                document.querySelectorAll('.industry-filter').forEach(el => {
                    el.addEventListener('change', fetchProjects);
                });

                document.querySelectorAll('.technology-filter').forEach(el => {
                    el.addEventListener('change', fetchProjects);
                });
            })
            .catch(error => {
                console.error('Error fetching projects:', error);
            });
    };

    const debouncedFetch = debounce(fetchProjects, 300);

    document.getElementById('project-search').addEventListener('input', debouncedFetch);

    document.querySelectorAll('.industry-filter').forEach(el => {
        el.addEventListener('change', fetchProjects);
    });

    document.querySelectorAll('.technology-filter').forEach(el => {
        el.addEventListener('change', fetchProjects);
    });

    document.getElementById('industry-search').addEventListener('input', debouncedFetch);
    document.getElementById('technology-search').addEventListener('input', debouncedFetch);
});