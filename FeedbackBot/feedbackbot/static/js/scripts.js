document.addEventListener("DOMContentLoaded", () => {
	const recordButton = document.getElementById("recordButton");
	const status = document.getElementById("status");
	const transcription = document.getElementById("transcription");

	let recorder;
	let gumStream;
	let isRecording = false;

	if (recordButton) {
		recordButton.onclick = () => {
			if (!isRecording) {
				startProcess();
			} else {
				stopProcess();
			}
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
				status.textContent = "Processing...";
				recordButton.textContent = "Stop";
				recordButton.classList.add("recording");
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
		status.textContent = "Processing stopped. Transcribing...";
		recordButton.textContent = "Start";
		recordButton.classList.remove("recording");

		recorder.exportWAV((blob) => {
			const formData = new FormData();
			formData.append("file", blob, "recording.wav");

			fetch("/transcribe/", {
				method: "POST",
				body: formData,
			})
				.then((response) => response.json())
				.then((data) => {
					transcription.textContent = data.text;
				})
				.catch((error) => {
					console.error("Error:", error);
					transcription.textContent = `Error transcribing the audio: ${error.message}`;
				});
		});
	}

	const fetchSummaryButton = document.getElementById("fetchSummaryButton");
	if (fetchSummaryButton) {
		fetchSummaryButton.onclick = () => {
			fetchSummary();
		};
	}

	function fetchSummary() {
		fetch("/summarise", {
			method: "GET",
		})
			.then((response) => response.json())
			.then((data) => {
				document.getElementById("summary").textContent =
					data.summary || "No summary available.";
				document.getElementById("keywords").textContent =
					data.keywords.join(", ") || "No keywords available.";
				document.getElementById("sentiment").textContent =
					`Sentiment: ${data.sentiment || "No sentiment data available."}`;
			})
			.catch((error) => {
				console.error("Error fetching summary:", error);
				document.getElementById("summary").textContent =
					`Error fetching the summary: ${error.message}`;
				document.getElementById("keywords").textContent =
					"Error fetching the keywords.";
				document.getElementById("sentiment").textContent =
					"Error fetching the sentiment.";
			});
	}
});
