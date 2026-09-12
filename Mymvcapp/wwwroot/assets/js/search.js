const startBtn = document.getElementById("startBtn");
const searchInput = document.getElementById("search-input");
const status = document.getElementById("status");
const stopBtn = document.getElementById("stopBtn");

let socket = null;
let mediaRecorder = null;
let audioChunks = [];
let recordingStream = null;
let stopTimer = null;


// =====================================================
// Connect WebSocket
// =====================================================

function connectWebSocket() {

    console.log("🔵 Connecting WebSocket...");

    const socketProtocol =
        window.location.protocol === "https:" ? "wss:" : "ws:";

    socket = new WebSocket(
        `${socketProtocol}//127.0.0.1:8000/ws/student-search`
    );


    socket.onopen = () => {

        console.log("🟢 WebSocket connected");

        status.textContent = "Connected";

    };


    socket.onmessage = (event) => {

        console.log(
            "📩 Server response:",
            event.data
        );

        const data = JSON.parse(event.data);

        handleServerResponse(data);
    };


    socket.onerror = (error) => {

        console.error(
            "❌ WebSocket error:",
            error
        );

        status.textContent =
            "WebSocket connection error";
    };


    socket.onclose = () => {

        console.log(
            "🔴 WebSocket disconnected"
        );

        status.textContent =
            "Disconnected";
    };
}


// =====================================================
// Handle backend response
// =====================================================

function handleServerResponse(data) {

    console.log(
        "📦 Response type:",
        data.type
    );


    if (data.type === "status") {

        status.textContent =
            data.message;

        return;
    }


    if (data.type === "transcript") {

        console.log(
            "🗣️ Transcript:",
            data.transcript
        );

        searchInput.value =
            data.search_term ||
            data.transcript;

        searchCandidate(data.search_term || data.transcript);

        return;
    }


    if (data.type === "results") {

        const students = Array.isArray(data.students)
            ? data.students
            : [];

        console.log(
            "👥 Candidates:",
            students
        );

        searchInput.value =
            data.search_term;

        status.textContent =
            data.message || `${students.length} candidate(s) found`;

        renderCandidates(students);

        return;
    }


    if (data.type === "error") {

        console.error(
            "❌ Backend error:",
            data.message
        );

        status.textContent =
            data.message;
    }
}


// =====================================================
// Microphone button
// =====================================================

startBtn.addEventListener(
    "click",
    async () => {

        try {

            console.log(
                "🎤 Microphone button clicked"
            );


            // -----------------------------------------
            // Make sure WebSocket is connected
            // -----------------------------------------

            if (
                !socket ||
                socket.readyState !== WebSocket.OPEN
            ) {

                console.log(
                    "🔵 WebSocket not connected"
                );

                connectWebSocket();

                // Give WebSocket time to connect
                await waitForWebSocket();
            }


            // -----------------------------------------
            // Get microphone
            // -----------------------------------------

            recordingStream =
                await navigator.mediaDevices.getUserMedia({
                    audio: true
                });


            console.log(
                "🎤 Microphone permission granted"
            );


            audioChunks = [];


            // -----------------------------------------
            // Create recorder
            // -----------------------------------------

            mediaRecorder =
                new MediaRecorder(recordingStream);


            mediaRecorder.ondataavailable =
                (event) => {

                    if (
                        event.data.size > 0
                    ) {

                        audioChunks.push(
                            event.data
                        );
                    }
                };


            // -----------------------------------------
            // Recording finished
            // -----------------------------------------

            mediaRecorder.onstop = async () => {

                    console.log("🛑 Recording stopped");

                    const audioBlob =
                        new Blob(
                            audioChunks,
                            {
                                type:mediaRecorder.mimeType
                            }
                        );

                        console.log("🎵 Audio size:",audioBlob.size );

                    // Stop microphone
                    recordingStream
                        .getTracks()
                        .forEach(
                            track =>
                                track.stop()
                        );

                    // ---------------------------------
                    // Send audio to FastAPI
                    // ---------------------------------

                    if (
                        socket &&
                        socket.readyState ===
                            WebSocket.OPEN
                    ) {

                        console.log(
                            "📤 Sending audio to backend..."
                        );

                        const audioBuffer =
                            await audioBlob.arrayBuffer();

                        socket.send(
                            audioBuffer
                        );

                        status.textContent =
                            "Processing voice...";
                    }

                    mediaRecorder = null;
                    recordingStream = null;

                };


            // -----------------------------------------
            // Start recording
            // -----------------------------------------

            mediaRecorder.start();

            startBtn.classList.add(
                "recording"
            );

            status.textContent =
                "🎤 Listening...";


            console.log(
                "🔴 Recording started"
            );


            // -----------------------------------------
            // Automatically stop after 5 seconds
            // -----------------------------------------

            stopTimer = setTimeout(() => {

                if (
                    mediaRecorder &&
                    mediaRecorder.state ===
                        "recording"
                ) {

                    mediaRecorder.stop();

                    startBtn.classList.remove(
                        "recording"
                    );
                }

            }, 5000);


        }
        catch (error) {

            console.error(
                "❌ Voice search error:",
                error
            );

            status.textContent =
                error.message;
        }

    }
);

stopBtn.addEventListener("click", stopRecording);

function stopRecording() {
    if (stopTimer) {
        clearTimeout(stopTimer);
        stopTimer = null;
    }

    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
        startBtn.classList.remove("recording");
        stopBtn.disabled = true;
        console.log("⏹️ Stop button clicked");
    }
}

function searchCandidate(fullname) {
    const value = fullname.trim();

    if (!value || !socket || socket.readyState !== WebSocket.OPEN) {
        return;
    }

    socket.send(JSON.stringify({
        action: "search",
        fullname: value
    }));

    status.textContent = "Searching...";
}

function renderCandidates(candidates) {
    const table = document.getElementById("candidateTable");
    const tbody = table ? table.querySelector("tbody") : null;

    if (!tbody) {
        return;
    }

    tbody.innerHTML = "";

    candidates.forEach((candidate) => {
        const row = document.createElement("tr");
        const values = [
            candidate.fullname,
            candidate.email,
            candidate.mobile,
            candidate.gender,
            candidate.position,
            candidate.qualification,
            candidate.experience,
            candidate.yearOfPassing,
            candidate.percentage,
            candidate.college,
            candidate.resume,
            candidate.status
        ];

        values.forEach((value) => {
            const cell = document.createElement("td");
            cell.textContent = value ?? "-";
            row.appendChild(cell);
        });

        tbody.appendChild(row);
    });
}


// =====================================================
// Wait for WebSocket connection
// =====================================================

function waitForWebSocket() {

    return new Promise(
        (resolve, reject) => {

            const timeout =
                setTimeout(() => {

                    reject(
                        new Error(
                            "WebSocket connection timeout"
                        )
                    );

                }, 5000);


            const check =
                setInterval(() => {

                    if (
                        socket &&
                        socket.readyState ===
                            WebSocket.OPEN
                    ) {

                        clearInterval(check);
                        clearTimeout(timeout);

                        resolve();
                    }


                    if (
                        socket &&
                        socket.readyState ===
                            WebSocket.CLOSED
                    ) {

                        clearInterval(check);
                        clearTimeout(timeout);

                        reject(
                            new Error(
                                "WebSocket connection failed"
                            )
                        );
                    }

                }, 100);

        }
    );
}