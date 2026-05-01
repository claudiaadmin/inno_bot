document.addEventListener("DOMContentLoaded", () => {
	const recordButton = document.getElementById("recordButton");
	const status = document.getElementById("status");
	const transcription = document.getElementById("transcription");

	let recorder;
	let gumStream;
	let isRecording = false;

	// Undo/redo state
	let lastFeedbackId = null;
	let undoneEntry = null; // { text, username, wasTyped }

	const pulseRing = document.getElementById("pulseRing");
	const transcriptionSection = document.getElementById("transcriptionSection");
	const usernameInput = document.getElementById("usernameInput");
	const actionButtons = document.getElementById("actionButtons");
	const undoButton = document.getElementById("undoButton");
	const redoButton = document.getElementById("redoButton");
	const startOverButton = document.getElementById("startOverButton");
	const doneButton = document.getElementById("doneButton");
	const doneScreen = document.getElementById("doneScreen");
	const addMoreButton = document.getElementById("addMoreButton");
	const recordingArea = document.getElementById("recordingArea");

	// Tab elements
	const tabRecord = document.getElementById("tabRecord");
	const tabType = document.getElementById("tabType");
	const panelRecord = document.getElementById("panelRecord");
	const panelType = document.getElementById("panelType");
	const feedbackText = document.getElementById("feedbackText");
	const submitTextButton = document.getElementById("submitTextButton");

	// Restore saved username from localStorage
	if (usernameInput) {
		const savedName = localStorage.getItem("feedbackbot_username");
		if (savedName) usernameInput.value = savedName;
		usernameInput.addEventListener("change", () => {
			localStorage.setItem("feedbackbot_username", usernameInput.value);
		});
	}

	// Tab switching
	if (tabRecord) {
		tabRecord.onclick = () => {
			tabRecord.classList.add("active");
			tabType.classList.remove("active");
			panelRecord.classList.remove("hidden");
			panelType.classList.add("hidden");
		};
	}
	if (tabType) {
		tabType.onclick = () => {
			tabType.classList.add("active");
			tabRecord.classList.remove("active");
			panelType.classList.remove("hidden");
			panelRecord.classList.add("hidden");
		};
	}

	// Submit typed feedback
	if (submitTextButton) {
		submitTextButton.onclick = () => {
			const text = feedbackText ? feedbackText.value.trim() : "";
			if (!text) return;

			const username = usernameInput ? usernameInput.value : "Anonymous";
			submitTextButton.disabled = true;
			submitTextButton.querySelector("span").textContent = "Submitting...";

			fetch("/feedback/", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ text, username }),
			})
				.then((response) => response.json())
				.then((data) => {
					lastFeedbackId = data.id;
					undoneEntry = null;
					if (redoButton) redoButton.classList.add("hidden");
					if (undoButton) undoButton.classList.remove("hidden");
					transcription.textContent = data.text;
					if (transcriptionSection) transcriptionSection.classList.add("visible");
					if (panelType) panelType.classList.add("hidden");
					if (panelRecord) panelRecord.classList.add("hidden");
					const tabs = document.querySelector(".input-mode-tabs");
					if (tabs) tabs.style.display = "none";
					submitTextButton.disabled = false;
					submitTextButton.querySelector("span").textContent = "Submit Feedback";
				})
				.catch((error) => {
					console.error("Error:", error);
					transcription.textContent = `Error submitting feedback: ${error.message}`;
					if (transcriptionSection) transcriptionSection.classList.add("visible");
					submitTextButton.disabled = false;
					submitTextButton.querySelector("span").textContent = "Submit Feedback";
				});
		};
	}

	if (recordButton) {
		recordButton.onclick = () => {
			if (!isRecording) {
				startProcess();
			} else {
				stopProcess();
			}
		};
	}

	function resetToInputMode() {
		if (transcriptionSection) transcriptionSection.classList.remove("visible");
		if (transcription) transcription.textContent = "";
		if (feedbackText) feedbackText.value = "";
		if (recordButton) recordButton.style.display = "";
		if (panelRecord) panelRecord.classList.remove("hidden");
		if (panelType) panelType.classList.add("hidden");
		if (tabRecord) { tabRecord.classList.add("active"); }
		if (tabType) { tabType.classList.remove("active"); }
		const tabs = document.querySelector(".input-mode-tabs");
		if (tabs) tabs.style.display = "";
		if (status) status.textContent = "Press the button to begin recording.";
		lastFeedbackId = null;
		undoneEntry = null;
		if (redoButton) redoButton.classList.add("hidden");
		if (undoButton) undoButton.classList.remove("hidden");
	}

	// Undo — delete the last submission from the server, go back to edit
	if (undoButton) {
		undoButton.onclick = () => {
			if (!lastFeedbackId) return;
			undoButton.disabled = true;

			fetch(`/feedback/${lastFeedbackId}`, { method: "DELETE" })
				.then((response) => {
					if (!response.ok) throw new Error("Failed to undo.");
					// Save for redo
					undoneEntry = {
						text: transcription ? transcription.textContent : "",
						username: usernameInput ? usernameInput.value : "Anonymous",
					};
					// Reset UI but pre-fill text area
					if (transcriptionSection) transcriptionSection.classList.remove("visible");
					if (feedbackText) feedbackText.value = undoneEntry.text;
					if (panelType) panelType.classList.remove("hidden");
					if (panelRecord) panelRecord.classList.add("hidden");
					if (tabType) tabType.classList.add("active");
					if (tabRecord) tabRecord.classList.remove("active");
					const tabs = document.querySelector(".input-mode-tabs");
					if (tabs) tabs.style.display = "";
					if (status) status.textContent = "Feedback removed. You can edit and resubmit.";
					lastFeedbackId = null;
					// Show redo button
					if (redoButton) redoButton.classList.remove("hidden");
					undoButton.disabled = false;
				})
				.catch((err) => {
					console.error("Undo error:", err);
					if (status) status.textContent = "Could not undo. Please try again.";
					undoButton.disabled = false;
				});
		};
	}

	// Redo — re-submit the undone feedback
	if (redoButton) {
		redoButton.onclick = () => {
			if (!undoneEntry || !undoneEntry.text) return;
			redoButton.disabled = true;

			fetch("/feedback/", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ text: undoneEntry.text, username: undoneEntry.username }),
			})
				.then((response) => response.json())
				.then((data) => {
					lastFeedbackId = data.id;
					if (transcription) transcription.textContent = data.text;
					if (transcriptionSection) transcriptionSection.classList.add("visible");
					if (panelType) panelType.classList.add("hidden");
					if (panelRecord) panelRecord.classList.add("hidden");
					const tabs = document.querySelector(".input-mode-tabs");
					if (tabs) tabs.style.display = "none";
					undoneEntry = null;
					redoButton.classList.add("hidden");
					if (undoButton) undoButton.classList.remove("hidden");
					redoButton.disabled = false;
				})
				.catch((err) => {
					console.error("Redo error:", err);
					if (status) status.textContent = "Could not redo. Please try again.";
					redoButton.disabled = false;
				});
		};
	}

	// Start Over — reset everything fresh
	if (startOverButton) {
		startOverButton.onclick = () => {
			resetToInputMode();
		};
	}

	// "Done" — show thank-you screen
	if (doneButton) {
		doneButton.onclick = () => {
			if (recordingArea) recordingArea.style.display = "none";
			if (doneScreen) doneScreen.classList.add("visible");
		};
	}

	// "Add More Feedback" — go back from done screen
	if (addMoreButton) {
		addMoreButton.onclick = () => {
			if (doneScreen) doneScreen.classList.remove("visible");
			if (recordingArea) recordingArea.style.display = "";
			resetToInputMode();
		};
	}

	function startProcess() {
		const constraints = { audio: true };

		navigator.mediaDevices
			.getUserMedia(constraints)
			.then((stream) => {
				gumStream = stream;
				const audioContext = new (
					window.AudioContext || window.webkitAudioContext
				)();
				const input = audioContext.createMediaStreamSource(stream);

				recorder = new Recorder(input, { numChannels: 1 });
				recorder.record();
				isRecording = true;
				status.textContent = "Recording in progress...";
				recordButton.querySelector(".record-label").textContent = "Stop Recording";
				recordButton.classList.add("recording");
				if (pulseRing) pulseRing.classList.add("active");
			})
			.catch((err) => {
				console.error("Error accessing audio devices:", err);
				status.textContent = `Error accessing audio devices: ${err.message}`;
			});
	}

	function stopProcess() {
		recorder.stop();
		gumStream.getAudioTracks()[0].stop();
		isRecording = false;
		status.textContent = "Transcribing your feedback...";
		recordButton.querySelector(".record-label").textContent = "Start Recording";
		recordButton.classList.remove("recording");
		if (pulseRing) pulseRing.classList.remove("active");

		recorder.exportWAV((blob) => {
			const formData = new FormData();
			formData.append("file", blob, "recording.wav");
			const username = usernameInput ? usernameInput.value : "";
			formData.append("username", username || "Anonymous");

			fetch("/transcribe/", {
				method: "POST",
				body: formData,
			})
				.then((response) => response.json())
				.then((data) => {
					lastFeedbackId = data.id;
					undoneEntry = null;
					if (redoButton) redoButton.classList.add("hidden");
					if (undoButton) undoButton.classList.remove("hidden");
					transcription.textContent = data.text;
					if (transcriptionSection) transcriptionSection.classList.add("visible");
					status.textContent = "Transcription complete!";
					recordButton.style.display = "none";
					if (panelRecord) panelRecord.classList.add("hidden");
					const tabs = document.querySelector(".input-mode-tabs");
					if (tabs) tabs.style.display = "none";
				})
				.catch((error) => {
					console.error("Error:", error);
					transcription.textContent = `Error transcribing the audio: ${error.message}`;
				});
		});
	}

	const fetchSummaryButton = document.getElementById("fetchSummaryButton");
	const dayFilter = document.getElementById("dayFilter");

	if (fetchSummaryButton) {
		fetchSummaryButton.onclick = () => {
			fetchSummary();
		};
	}

	function fetchSummary() {
		const section = document.getElementById("summarySection");
		section.innerHTML = '<p class="placeholder-text">Loading summary...</p>';

		const dayValue = dayFilter ? dayFilter.value : "";
		const url = dayValue ? `/summarise/?day=${encodeURIComponent(dayValue)}` : "/summarise/";

		fetch(url, { method: "GET" })
			.then((response) => response.json())
			.then((data) => {
				renderSummary(data, section);
			})
			.catch((error) => {
				console.error("Error fetching summary:", error);
				section.innerHTML = `<p class="placeholder-text">Error fetching summary: ${error.message}</p>`;
			});
	}

	function renderSummary(data, section) {
		section.innerHTML = "";

		if (!data.days || data.days.length === 0) {
			section.innerHTML = '<p class="placeholder-text">No feedback data available for the selected filter.</p>';
			return;
		}

		data.days.forEach((day) => {
			const dayHeader = document.createElement("h2");
			dayHeader.className = "day-header";
			dayHeader.textContent = day.day;
			section.appendChild(dayHeader);

			day.groups.forEach((group) => {
				const card = document.createElement("div");
				card.className = "result-card";

				const groupTitle = document.createElement("h3");
				groupTitle.textContent = group.group;
				card.appendChild(groupTitle);

				const summaryLabel = document.createElement("h4");
				summaryLabel.className = "result-label";
				summaryLabel.textContent = "Summary";
				card.appendChild(summaryLabel);

				const summaryText = document.createElement("p");
				summaryText.textContent = group.summary || "No summary available.";
				card.appendChild(summaryText);

				const keywordsLabel = document.createElement("h4");
				keywordsLabel.className = "result-label";
				keywordsLabel.textContent = "Keywords";
				card.appendChild(keywordsLabel);

				const keywordsText = document.createElement("p");
				keywordsText.className = "keywords";
				keywordsText.textContent =
					group.keywords && group.keywords.length > 0
						? group.keywords.join(", ")
						: "No keywords available.";
				card.appendChild(keywordsText);

				const sentimentLabel = document.createElement("h4");
				sentimentLabel.className = "result-label";
				sentimentLabel.textContent = "Sentiment";
				card.appendChild(sentimentLabel);

				const sentimentText = document.createElement("p");
				sentimentText.className = "sentiment";
				sentimentText.textContent = group.sentiment || "No sentiment data.";
				card.appendChild(sentimentText);

				section.appendChild(card);
			});
		});
	}
});
