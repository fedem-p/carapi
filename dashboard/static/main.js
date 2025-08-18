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
});
