
const API_URL = "http://127.0.0.1:8000";

// HTML elements
const fileInput = document.getElementById("fileInput");
const fileStatus = document.getElementById("fileStatus");
const domainSelect = document.getElementById("domainSelect");
const uploadButton = document.getElementById("uploadButton");
const processingStatus = document.getElementById("processingStatus");

const askButton = document.getElementById("askButton");
const questionInput = document.getElementById("questionInput");
const questionDomain = document.getElementById("questionDomain");
const answerResult = document.getElementById("answerResult");
const sourceResult = document.getElementById("sourceResult");

// Display selected filename
fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];

    fileStatus.textContent = file
        ? `Selected: ${file.name}`
        : "No document selected.";
});

// Upload and process document
uploadButton.addEventListener("click", async () => {
    const file = fileInput.files[0];

    if (!file) {
        processingStatus.textContent =
            "Please select a document first.";
        return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("domain", domainSelect.value);

    uploadButton.disabled = true;
    uploadButton.textContent = "Uploading...";
    processingStatus.textContent = "Processing your document...";

    try {
        const response = await fetch(`${API_URL}/ingest`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || data.message || "Document processing failed."
            );
        }

        processingStatus.textContent =
            data.message || "Document processed successfully.";

        const chunkCount = data.chunk_count ?? data.chunks_stored;

        if (chunkCount !== undefined) {
            processingStatus.textContent +=
                ` Chunks stored: ${chunkCount}.`;
        }

    } catch (error) {
        processingStatus.textContent =
            `Upload failed: ${error.message}`;

    } finally {
        uploadButton.disabled = false;
        uploadButton.textContent = "Upload and Process";
    }
});

// Ask a question
askButton.addEventListener("click", async () => {
    const question = questionInput.value.trim();

    if (!question) {
        answerResult.textContent = "Please enter a question.";
        return;
    }

    askButton.disabled = true;
    askButton.textContent = "Searching...";
    answerResult.textContent = "Searching the knowledge base...";
    sourceResult.textContent = "Retrieving relevant sources...";

    try {
        const response = await fetch(`${API_URL}/query`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question,
                domain: questionDomain.value
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || data.message || "Question retrieval failed."
            );
        }

        answerResult.textContent =
            data.answer || "No answer was returned by the backend.";

        const sources = data.sources || data.results || [];

        if (Array.isArray(sources) && sources.length > 0) {
            sourceResult.textContent = sources.map((source, index) => {
                if (typeof source === "string") {
                    return `${index + 1}. ${source}`;
                }

                const filename =
                    source.source ||
                    source.filename ||
                    source.metadata?.source ||
                    "Unknown document";

                const content =
                    source.text ||
                    source.content ||
                    "";

                return `${index + 1}. Source: ${filename}\n${content}`;
            }).join("\n\n");

        } else {
            sourceResult.textContent =
                data.source || "No source details returned.";
        }

    } catch (error) {
        answerResult.textContent =
            `Unable to retrieve answer: ${error.message}`;

        sourceResult.textContent =
            "Please check the backend connection.";

    } finally {
        askButton.disabled = false;
        askButton.textContent = "Ask AI";
    }
});
