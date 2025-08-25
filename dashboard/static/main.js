document.addEventListener('DOMContentLoaded', function() {
    const startBtn = document.getElementById('start-btn');
    const progressBar = document.getElementById('progress-bar');
    const progressDetails = document.getElementById('progress-details');
    const resultsDiv = document.getElementById('results');

    let lastProgress = 0;
    let lastScraping = false;

    function updateProgress() {
        fetch('/progress')
            .then(res => res.json())
            .then(data => {
                progressBar.style.width = data.progress + '%';
                progressDetails.textContent = data.details;
                // Only fetch results if just finished (progress 100 and scraping false)
                if (data.progress === 100 && !data.scraping && (lastProgress !== 100 || lastScraping)) {
                    fetchResults();
                }
                lastProgress = data.progress;
                lastScraping = data.scraping;
            });
    }

    function fetchResults() {
        fetch('/results')
            .then(res => res.text())
            .then(html => {
                resultsDiv.innerHTML = html;
            });
    }

    startBtn.addEventListener('click', function() {
        fetch('/start-scrape', {method: 'POST'})
            .then(res => res.json())
            .then(data => {
                if (data.status === 'started') {
                    progressBar.style.width = '0%';
                    progressDetails.textContent = 'Starting...';
                    resultsDiv.innerHTML = '<p>Scraping in progress...</p>';
                }
            });
    });

    // Poll every 5 seconds (5000 ms)
    setInterval(updateProgress, 5000);

    // --- Settings Panel Logic ---
    const settingsForm = document.getElementById('settings-form');
    const statusSpan = document.getElementById('settings-status');

    // --- Slim Select initialization ---
    let bodySelect, fuelSelect;
    if (window.SlimSelect) {
        bodySelect = new SlimSelect({ select: '#filter-body' });
        fuelSelect = new SlimSelect({ select: '#filter-fuel' });
    }

    function loadSettings() {
        fetch('/config')
            .then(res => res.json())
            .then(cfg => {
                // Set values for Slim Select multiselects if available
                if (bodySelect) bodySelect.setSelected(cfg.filters.body || []);
                if (fuelSelect) fuelSelect.setSelected(cfg.filters.fuel || []);
                document.getElementById('filter-min-year').value = cfg.filters.min_year || '';
                document.getElementById('filter-kmto').value = cfg.filters.kmto || '';
                document.getElementById('filter-min-power').value = cfg.filters.min_power || '';
                document.getElementById('filter-max-price').value = cfg.filters.max_price || '';
                document.getElementById('filter-min-seats').value = cfg.filters.min_seats || '';
                document.getElementById('filter-sort').value = cfg.filters.sort || '';
                document.getElementById('num-pages').value = cfg.num_pages || '';
                document.getElementById('scoring-profiles').value = JSON.stringify(cfg.scoring_profiles, null, 2);
                document.getElementById('excluded-cars').value = JSON.stringify(cfg.excluded_cars, null, 2);
            });
    }

    settingsForm.addEventListener('submit', function(e) {
        e.preventDefault();
        // Use SlimSelect API to get all selected values for body and fuel
        const bodyValues = bodySelect ? bodySelect.getSelected() : Array.from(document.getElementById('filter-body').selectedOptions).map(o => o.value);
        const fuelValues = fuelSelect ? fuelSelect.getSelected() : Array.from(document.getElementById('filter-fuel').selectedOptions).map(o => o.value);
        // Get the value of the sort select
        const sortValue = document.getElementById('filter-sort').value;
        const filters = {
            body: bodyValues,
            min_year: document.getElementById('filter-min-year').value,
            kmto: document.getElementById('filter-kmto').value,
            min_power: document.getElementById('filter-min-power').value,
            max_price: document.getElementById('filter-max-price').value,
            min_seats: document.getElementById('filter-min-seats').value,
            fuel: fuelValues,
            sort: sortValue
        };
        let scoring_profiles, excluded_cars;
        try {
            scoring_profiles = JSON.parse(document.getElementById('scoring-profiles').value);
            excluded_cars = JSON.parse(document.getElementById('excluded-cars').value);
        } catch (err) {
            statusSpan.textContent = 'Invalid JSON in scoring profiles or excluded cars!';
            statusSpan.style.color = 'red';
            return;
        }
        const num_pages = parseInt(document.getElementById('num-pages').value, 10);
        fetch('/config', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({filters, num_pages, scoring_profiles, excluded_cars})
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                statusSpan.textContent = 'Settings saved!';
                statusSpan.style.color = 'green';
            } else {
                statusSpan.textContent = 'Error saving settings!';
                statusSpan.style.color = 'red';
            }
        })
        .catch(() => {
            statusSpan.textContent = 'Error saving settings!';
            statusSpan.style.color = 'red';
        });
    });

    // --- Send Email button logic ---
    const sendEmailBtn = document.getElementById('send-email-btn');
    function setSendEmailEnabled(enabled) {
        if (sendEmailBtn) sendEmailBtn.disabled = !enabled;
    }
    setSendEmailEnabled(false);

    // Enable send email button when results are available
    function checkResultsAndEnableEmail() {
        // Only enable if scraping is finished and results are available
        const noResults = resultsDiv.querySelector('p') && resultsDiv.querySelector('p').textContent.includes('No results yet.');
        const scraping = progressDetails.textContent.includes('Scraping') || progressDetails.textContent.includes('Starting') || progressBar.style.width !== '100%';
        setSendEmailEnabled(!noResults && !scraping && resultsDiv.innerText.trim() !== '');
    }

    // Patch fetchResults to enable button after loading
    const origFetchResults = fetchResults;
    fetchResults = function() {
        origFetchResults();
        setTimeout(checkResultsAndEnableEmail, 500); // Wait for DOM update
    };

    // Also check after progress updates
    setInterval(checkResultsAndEnableEmail, 2000);

    if (sendEmailBtn) {
        sendEmailBtn.addEventListener('click', function() {
            sendEmailBtn.disabled = true;
            sendEmailBtn.textContent = 'Sending...';
            fetch('/notify', { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        sendEmailBtn.textContent = 'Email Sent!';
                        setTimeout(() => {
                            sendEmailBtn.textContent = 'Send Email';
                            setSendEmailEnabled(true);
                        }, 2000);
                    } else {
                        let errMsg = 'Failed to send email.';
                        sendEmailBtn.textContent = 'Error: ' + errMsg;
                        setTimeout(() => {
                            sendEmailBtn.textContent = 'Send Email';
                            setSendEmailEnabled(true);
                        }, 3500);
                    }
                })
                .catch(() => {
                    sendEmailBtn.textContent = 'Error!';
                    setTimeout(() => {
                        sendEmailBtn.textContent = 'Send Email';
                        setSendEmailEnabled(true);
                    }, 2000);
                });
        });
    }

    // Collapsible logic for settings
    document.querySelectorAll('.collapsible').forEach(btn => {
        btn.addEventListener('click', function() {
            const target = document.getElementById(this.dataset.target);
            if (target.style.display === 'none' || !target.style.display) {
                target.style.display = 'block';
                this.textContent = this.textContent.replace('►', '▼');
            } else {
                target.style.display = 'none';
                this.textContent = this.textContent.replace('▼', '►');
            }
        });
    });
    // Set initial state: options open, others collapsed
    document.querySelectorAll('.collapsible').forEach(btn => {
        const target = document.getElementById(btn.dataset.target);
        if (btn.classList.contains('open')) {
            target.style.display = 'block';
            btn.textContent = btn.textContent.replace('►', '▼');
        } else {
            target.style.display = 'none';
            btn.textContent = btn.textContent.replace('▼', '►');
        }
    });

    loadSettings();
});
