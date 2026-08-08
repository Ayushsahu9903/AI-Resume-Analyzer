async function runMatching() {

    const status = document.getElementById("status-message");

    status.innerText = "Analyzing resumes...";

    try {

        const response = await fetch("/matching");

        if (!response.ok) {
            throw new Error("Matching request failed");
        }

        const data = await response.json();

        status.innerText = "Resume analysis completed.";

        displayData(data);

    } catch (error) {

        status.innerText =
            "Unable to run matching. Check the API.";

        console.error(error);
    }
}


async function runExtraction() {

    const status = document.getElementById("status-message");

    status.innerText = "Extracting job requirements...";

    try {

        const response = await fetch("/extraction");

        if (!response.ok) {
            throw new Error("Extraction request failed");
        }

        const data = await response.json();

        status.innerText =
            "Job requirements extracted successfully.";

        displayData(data);

    } catch (error) {

        status.innerText =
            "Unable to extract job information.";

        console.error(error);
    }
}


async function loadCandidates() {

    const container =
        document.getElementById("results-container");

    container.innerHTML = `
        <div class="empty-state">
            Loading top candidates...
        </div>
    `;

    try {

        const response = await fetch("/top_resumes");

        if (!response.ok) {
            throw new Error("Candidate request failed");
        }

        const data = await response.json();

        displayCandidates(data);

    } catch (error) {

        container.innerHTML = `
            <div class="empty-state">
                Unable to load candidates.
                Please check the API.
            </div>
        `;

        console.error(error);
    }
}


function displayData(data) {

    console.log("API response:", data);

    const scoreElement =
        document.getElementById("score");

    const progress =
        document.getElementById("progress-bar");

    let score = null;

    if (typeof data === "number") {
        score = data;
    }

    if (data && typeof data === "object") {

        score =
            data.score ||
            data.match_score ||
            data.similarity ||
            data.match_percentage;
    }

    if (score !== null) {

        score = parseFloat(score);

        if (!isNaN(score)) {

            if (score <= 1) {
                score *= 100;
            }

            score = Math.round(score);

            scoreElement.innerText =
                score + "%";

            progress.style.width =
                score + "%";
        }
    }
}


function displayCandidates(data) {

    const container =
        document.getElementById("results-container");

    let candidates = data;

    if (data && data.top_resumes) {
        candidates = data.top_resumes;
    }

    if (data && data.results) {
        candidates = data.results;
    }

    if (!Array.isArray(candidates)) {

        container.innerHTML = `
            <div class="empty-state">
                API returned data successfully.
                Open the browser console to inspect it.
            </div>
        `;

        console.log(data);

        return;
    }

    if (candidates.length === 0) {

        container.innerHTML = `
            <div class="empty-state">
                No candidates found.
            </div>
        `;

        return;
    }

    const rows = candidates.map((candidate, index) => {

        const name =
            candidate.name ||
            candidate.Name ||
            candidate.resume ||
            candidate.filename ||
            `Candidate ${index + 1}`;

        const score =
            candidate.score ||
            candidate.match_score ||
            candidate.similarity ||
            "-";

        return `
            <tr>
                <td>${index + 1}</td>
                <td>${name}</td>
                <td>${score}</td>
            </tr>
        `;

    }).join("");

    container.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Candidate</th>
                    <th>Match Score</th>
                </tr>
            </thead>

            <tbody>
                ${rows}
            </tbody>
        </table>
    `;
}
