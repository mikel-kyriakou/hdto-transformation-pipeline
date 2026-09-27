const form = document.getElementById("transform-form");
const submitButton = document.getElementById("submit-button");
const resultCard = document.getElementById("result-card");
const errorMessage = document.getElementById("error-message");
const classBreakdown = document.getElementById("class-breakdown");
const breakdownToggle = document.getElementById("class-breakdown-toggle");
const downloadButton = document.getElementById("download-button");
let currentOutput = null;

function setMetric(id, value, suffix = "") {
    document.getElementById(id).textContent = value == null ? "-" : `${value}${suffix}`;
}

function renderResult(payload) {
    const metrics = payload.metrics || {};
    currentOutput = { content: payload.content, format: payload.format };
    document.getElementById("rdfContent").textContent = payload.content;

    setMetric("metric-source", metrics.identified_source);
    setMetric("metric-duration", metrics.duration_s, " s");
    setMetric("metric-processed", metrics.records_processed);
    setMetric("metric-valid", metrics.records_valid);
    setMetric("metric-invalid", metrics.records_invalid);
    setMetric("metric-triples", metrics.triples_generated);

    const classList = document.getElementById("class-breakdown-list");
    classList.replaceChildren();
    const classCounts = metrics.items_per_class || {};

    for (const [className, count] of Object.entries(classCounts)) {
        const item = document.createElement("li");
        const name = document.createElement("span");
        const badge = document.createElement("span");
        item.className = "list-group-item d-flex justify-content-between align-items-center";
        name.textContent = className;
        badge.className = "badge text-bg-primary rounded-pill";
        badge.textContent = count;
        item.append(name, badge);
        classList.append(item);
    }

    const hasClassCounts = Object.keys(classCounts).length > 0;
    breakdownToggle.hidden = !hasClassCounts;
    if (hasClassCounts) {
        breakdownToggle.classList.remove("d-none");
        breakdownToggle.textContent = "Show items per class";
        breakdownToggle.setAttribute("aria-expanded", "false");
        bootstrap.Collapse.getOrCreateInstance(classBreakdown, { toggle: false }).hide();
    }

    downloadButton.disabled = false;
    resultCard.classList.remove("d-none");
    resultCard.scrollIntoView({ behavior: "smooth", block: "start" });
}

classBreakdown.addEventListener("show.bs.collapse", () => {
    breakdownToggle.textContent = "Hide items per class";
    breakdownToggle.setAttribute("aria-expanded", "true");
});

classBreakdown.addEventListener("hide.bs.collapse", () => {
    breakdownToggle.textContent = "Show items per class";
    breakdownToggle.setAttribute("aria-expanded", "false");
});

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const fileInput = document.getElementById("input-file");
    const formatInput = document.getElementById("input-format");
    if (fileInput.files.length === 0) {
        errorMessage.textContent = "Please select a JSON file.";
        errorMessage.hidden = false;
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    formData.append("output_format", formatInput.value);

    resultCard.classList.add("d-none");
    errorMessage.hidden = true;
    submitButton.disabled = true;
    submitButton.textContent = "Transforming...";
    downloadButton.disabled = true;
    currentOutput = null;

    try {
        const response = await fetch("/generate-rdf", { method: "POST", body: formData });
        const payload = await response.json();
        if (!response.ok) {
            const detail = payload?.detail;
            const message = Array.isArray(detail)
                ? detail.map((item) => item.msg || item).join("; ")
                : detail || "Unknown error";
            throw new Error(message);
        }

        renderResult(payload);
    } catch (error) {
        console.error(error);
        errorMessage.textContent = error instanceof Error
            ? error.message
            : "An error occurred during the transformation.";
        errorMessage.hidden = false;
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = "Transform";
    }
});

downloadButton.addEventListener("click", () => {
    if (!currentOutput) return;

    const extension = currentOutput.format === "text/turtle" ? "ttl" : "rdf";
    const blob = new Blob([currentOutput.content], { type: currentOutput.format });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `output.${extension}`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.setTimeout(() => window.URL.revokeObjectURL(url), 1000);
});
