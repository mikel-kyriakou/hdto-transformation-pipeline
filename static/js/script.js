const form = document.getElementById("transform-form");
const submitButton = document.getElementById("submit-button");
const resultCard = document.getElementById("result-card");
const errorMessage = document.getElementById("error-message");
const classBreakdown = document.getElementById("class-breakdown");
const classBreakdownPanel = document.getElementById("class-breakdown-panel");
const downloadButton = document.getElementById("download-button");
const viewButton = document.getElementById("view-button");
const viewGraphButton = document.getElementById("view-graph-button");
const invalidRecordsButton = document.getElementById("invalid-records-button");
const invalidRecordsList = document.getElementById("invalid-records-list");
const graphModal = document.getElementById("graphModal");
const graphContainer = document.getElementById("rdf-graph");
const fileButton = document.getElementById("file-button");
const textButton = document.getElementById("text-button");
const fileInput = document.getElementById("input-file");
const textInput = document.getElementById("input-text");
const customInputTemplate = {
    id: "object-001",
    title: "Ancient Greek vase",
    object_type: "Amphora",
    creator: "Unknown potter",
    date_of_creation: "5th century BCE",
    place_of_creation: "Athens, Greece",
    material: "Terracotta",
    dimensions: "Height: 35 cm; diameter: 22 cm",
    cultural_period: "Classical Greece",
    digital_file: {
        file_url: "https://example.com/ancient-greek-vase.glb",
        file_type: "3D model",
        format: "glTF",
        representation: "ancient-greek-vase.glb",
    },
};
const customInputTemplateJson = JSON.stringify(customInputTemplate, null, 2);
let currentOutput = null;
let rdfGraph = null;
const errorToast = document.getElementById("error-toast");
const errorToastMessage = document.getElementById("error-toast-message");

document.getElementById("customInputTemplateContent").textContent = customInputTemplateJson;
document.getElementById("download-custom-input-template").addEventListener("click", () => {
    const blob = new Blob([customInputTemplateJson], { type: "application/json" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "custom-input-template.json";
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.setTimeout(() => window.URL.revokeObjectURL(url), 1000);
});

function setInputMode(mode) {
    const useFile = mode === "file";
    fileInput.disabled = !useFile;
    fileInput.required = useFile;
    textInput.disabled = useFile;
    textInput.required = !useFile;
    fileButton.classList.toggle("active", useFile);
    textButton.classList.toggle("active", !useFile);
    fileButton.setAttribute("aria-pressed", String(useFile));
    textButton.setAttribute("aria-pressed", String(!useFile));
}

fileButton.addEventListener("click", () => setInputMode("file"));
textButton.addEventListener("click", () => setInputMode("text"));

function setMetric(id, value, suffix = "") {
    document.getElementById(id).textContent = value == null ? "-" : `${value}${suffix}`;
}

function renderInvalidRecords(records) {
    invalidRecordsList.replaceChildren();

    records.forEach((record, position) => {
        const item = document.createElement("section");
        item.className = "list-group-item";

        const heading = document.createElement("h6");
        heading.className = "mb-2";
        heading.textContent = `Object ${record.index}`;

        const missingFieldsLabel = document.createElement("p");
        missingFieldsLabel.className = "mb-1 fw-semibold";
        missingFieldsLabel.textContent = "Missing fields";

        const missingFields = document.createElement("ul");
        missingFields.className = "mb-3";
        for (const field of Array.isArray(record.missing_fields) ? record.missing_fields : []) {
            const fieldItem = document.createElement("li");
            fieldItem.textContent = field;
            missingFields.append(fieldItem);
        }

        const contentId = `invalid-record-content-${position}`;
        const contentButton = document.createElement("button");
        contentButton.type = "button";
        contentButton.className = "btn btn-sm btn-outline-secondary";
        contentButton.dataset.bsToggle = "collapse";
        contentButton.dataset.bsTarget = `#${contentId}`;
        contentButton.setAttribute("aria-expanded", "false");
        contentButton.setAttribute("aria-controls", contentId);
        contentButton.textContent = "Show record content";

        const contentPanel = document.createElement("div");
        contentPanel.id = contentId;
        contentPanel.className = "collapse mt-2";

        const content = document.createElement("pre");
        content.className = "bg-body-tertiary border rounded p-3 mb-0";
        content.textContent = JSON.stringify(record.content, null, 2) ?? String(record.content ?? "");

        contentPanel.append(content);
        item.append(heading, missingFieldsLabel, missingFields, contentButton, contentPanel);
        invalidRecordsList.append(item);
    });

    invalidRecordsButton.classList.toggle("d-none", records.length === 0);
}

function renderResult(payload) {
    const metrics = payload.metrics || {};
    const invalidRecords = Array.isArray(metrics.invalid_records_data) ? metrics.invalid_records_data : [];
    currentOutput = { content: payload.content, format: payload.format, triples: payload.triples || [] };
    if (rdfGraph) {
        rdfGraph.destroy();
        rdfGraph = null;
    }
    document.getElementById("rdfContent").textContent = payload.content;

    setMetric("metric-source", metrics.identified_source);
    setMetric("metric-duration", metrics.duration_s, " s");
    setMetric("metric-processed", metrics.records_processed);
    setMetric("metric-valid", metrics.records_valid);
    setMetric("metric-invalid", metrics.records_invalid);
    setMetric("metric-triples", metrics.triples_generated);
    renderInvalidRecords(invalidRecords);

    const classList = document.getElementById("class-breakdown-list");
    classList.replaceChildren();
    const classCounts = metrics.items_per_class || {};

    for (const [className, count] of Object.entries(classCounts)) {
        const item = document.createElement("li");
        const name = document.createElement("span");
        const badge = document.createElement("span");
        item.className = "list-group-item d-flex justify-content-between align-items-center";
        name.textContent = className;
        badge.className = "badge text-bg-secondary rounded-pill";
        badge.textContent = count;
        item.append(name, badge);
        classList.append(item);
    }

    const hasClassCounts = Object.keys(classCounts).length > 0;
    classBreakdown.classList.toggle("d-none", !hasClassCounts);
    if (hasClassCounts) {
        bootstrap.Collapse.getOrCreateInstance(classBreakdownPanel, { toggle: false }).hide();
    }

    downloadButton.disabled = false;
    viewButton.disabled = false;
    viewGraphButton.disabled = false;
    resultCard.classList.remove("d-none");
    resultCard.scrollIntoView({ behavior: "smooth", block: "start" });
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const formatInput = document.getElementById("input-format");
    let inputFile;
    if (fileInput.disabled) {
        const text = textInput.value.trim();
        if (!text) {
            errorMessage.textContent = "Please enter JSON text.";
            errorMessage.hidden = false;
            return;
        }
        inputFile = new File([text], "input.json", { type: "application/json" });
    } else if (fileInput.files.length > 0) {
        inputFile = fileInput.files[0];
    } else {
        errorMessage.textContent = "Please select a JSON file.";
        errorMessage.hidden = false;
        return;
    }

    const formData = new FormData();
    formData.append("file", inputFile);
    formData.append("output_format", formatInput.value);

    errorMessage.hidden = true;
    submitButton.disabled = true;
    submitButton.textContent = "Transforming...";
    downloadButton.disabled = true;
    currentOutput = null;

    try {
        const response = await fetch("/hdto/generate-rdf", { method: "POST", body: formData });
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
        const message = error instanceof Error
            ? error.message
            : "An error occurred during the transformation.";
        showErrorToast(message);
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

function compactUri(uri) {
    const separator = Math.max(uri.lastIndexOf("#"), uri.lastIndexOf("/"));
    return uri.slice(separator + 1) || uri;
}

function renderGraph() {
    if (!currentOutput || currentOutput.triples.length === 0) {
        graphContainer.textContent = "No RDF triples are available to display.";
        return;
    }

    const nodeData = new Map();
    const edgeData = [];
    const addNode = (id, label, kind) => {
        if (nodeData.has(id)) return;
        const isLiteral = kind === "Literal";
        const shortLabel = isLiteral ? label : compactUri(label);
        nodeData.set(id, {
            data: {
                id,
                label: shortLabel.length > 42 ? `${shortLabel.slice(0, 39)}...` : shortLabel,
                details: `${label} (${kind})`,
                kind: isLiteral ? "literal" : kind === "BNode" ? "blank" : "resource",
            },
        });
    };

    currentOutput.triples.forEach((triple, index) => {
        addNode(triple.subject, triple.subject_label, triple.subject_kind);
        addNode(triple.object, triple.object_label, triple.object_kind);
        edgeData.push({
            data: {
                id: `triple-${index}`,
                source: triple.subject,
                target: triple.object,
                label: compactUri(triple.predicate_label),
                details: triple.predicate_label,
            },
        });
    });

    graphContainer.replaceChildren();
    if (rdfGraph) rdfGraph.destroy();
    rdfGraph = cytoscape({
        container: graphContainer,
        elements: [...nodeData.values(), ...edgeData],
        style: [
            {
                selector: "node",
                style: {
                    label: "data(label)",
                    "font-size": 12,
                    "text-wrap": "wrap",
                    "text-max-width": 150,
                    "text-valign": "center",
                    "text-halign": "center",
                    color: "#222222",
                    "background-color": "#a9574e",
                    width: "label",
                    height: "label",
                    padding: "12px",
                    "border-width": 1,
                    "border-color": "#732526",
                },
            },
            { selector: 'node[kind = "literal"]', style: { shape: "round-rectangle", "background-color": "#f4df9b", "border-color": "#ad8735" } },
            { selector: 'node[kind = "blank"]', style: { shape: "diamond", "background-color": "#d8e2e8", "border-color": "#788b98" } },
            {
                selector: "edge",
                style: {
                    width: 1.5,
                    "line-color": "#777777",
                    "target-arrow-color": "#777777",
                    "target-arrow-shape": "triangle",
                    "curve-style": "bezier",
                    label: "data(label)",
                    "font-size": 10,
                    color: "#383838",
                    "text-background-color": "#fbfaf8",
                    "text-background-opacity": 1,
                    "text-background-padding": 2,
                    "text-rotation": "autorotate",
                },
            },
            { selector: ":selected", style: { "overlay-color": "#732526", "overlay-opacity": 0.15 } },
        ],
        layout: { name: "cose", animate: false, padding: 30, nodeRepulsion: 7000, idealEdgeLength: 110 },
        minZoom: 0.2,
        maxZoom: 3,
        wheelSensitivity: 0.2,
    });

    rdfGraph.nodes().forEach((node) => node.qtip?.({ content: node.data("details") }));
    rdfGraph.on("mouseover", "node, edge", (event) => {
        graphContainer.title = event.target.data("details");
    });
}

function showGraph() {
    requestAnimationFrame(() => {
        const shouldFit = !rdfGraph;
        if (shouldFit) renderGraph();
        rdfGraph?.resize();
        if (shouldFit) rdfGraph?.fit(undefined, 30);
    });
}

function showErrorToast(message) {
    errorToastMessage.textContent = message;
    const toast = bootstrap.Toast.getOrCreateInstance(errorToast, { delay: 5000 });
    toast.show();
}

graphModal.addEventListener("shown.bs.modal", showGraph);

document.getElementById("fit-graph-button").addEventListener("click", () => {
    rdfGraph?.fit(undefined, 30);
});
