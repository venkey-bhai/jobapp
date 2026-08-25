const form = document.getElementById("jobForm");
console.log("FORM:", form);


const viewCandidatesBtn = document.getElementById("viewCandidatesBtn");
const candidateListSection = document.getElementById("candidateListSection");
const candidateListMessage = document.getElementById("candidateListMessage");
const candidateTableBody = document.querySelector("#candidateTable tbody");

if (viewCandidatesBtn) {
    
    viewCandidatesBtn.addEventListener("click", async () => {

        console.log("SEARCH BUTTON CLICKED");
        
        candidateListSection.style.display = "block";
        candidateListMessage.textContent = "Loading candidates...";
        candidateTableBody.innerHTML = "";

        try {
            const response = await fetch("http://127.0.0.1:8000/candidates");

            if (!response.ok) {
                throw new Error("Could not load candidates.");
            }

            const data = await response.json();
            const candidates = data.candidates || [];

            if (candidates.length === 0) {
                candidateListMessage.textContent = "No candidates found.";
                return;
            }

            candidateListMessage.textContent = "";

            candidates.forEach((candidate) => {

                const row = document.createElement("tr");

                row.innerHTML = `
                    <td>${candidate.fullname || "-"}</td>
                    <td>${candidate.email || "-"}</td>
                    <td>${candidate.mobile || "-"}</td>
                    <td>${candidate.position || "-"}</td>
                    <td>${candidate.qualification || "-"}</td>
                    <td>${candidate.experience || "-"}</td>
                    <td>${candidate.yearOfPassing || "-"}</td>
                    <td>${candidate.percentage || "-"}</td>
                    <td>${candidate.college || "-"}</td>
                    <td>${candidate.resume || "-"}</td>
                    <td>${candidate.month || "-"}</td>
                `;

                candidateTableBody.appendChild(row);
            });

        } catch (error) {

            candidateListMessage.textContent = error.message;

        }

    });

}


form.addEventListener("submit", async function (event) {

    event.preventDefault();

    const resumeInput = document.getElementById("resume");

    if (!resumeInput.files.length) {
        alert("Please select your resume.");
        return;
    }

    const formData = new FormData();

    formData.append(
        "fullname",
        document.getElementById("fullname").value
    );

    formData.append(
        "email",
        document.getElementById("email").value
    );

    formData.append(
        "mobile",
        document.getElementById("mobile").value
    );

    formData.append(
        "position",
        document.getElementById("position").value
    );

    formData.append(
        "qualification",
        document.getElementById("qualification").value
    );

    formData.append(
        "experience",
        document.getElementById("experience").value
    );

    formData.append(
        "yearOfPassing",
        document.getElementById("yearOfPassing").value
    );

    formData.append(
        "percentage",
        document.getElementById("percentage").value
    );

    formData.append(
        "college",
        document.getElementById("college").value
    );

    formData.append(
        "primarySkills",
        document.getElementById("primarySkills").value
    );

    formData.append(
        "secondarySkills",
        document.getElementById("secondarySkills").value
    );

    formData.append(
        "languagesKnown",
        document.getElementById("languagesKnown").value
    );

    // IMPORTANT
    formData.append(
        "resume",
        resumeInput.files[0]
    );

    try {
        const response = await fetch("http://127.0.0.1:8000/candidates", {
            method: "POST",
            body: formData,
        });

        const result = await response.json();
        document.getElementById("loader").style.display = "none";

        if (!response.ok) {
            throw new Error(result.detail || "Application could not be submitted.");
        }

        const applicationSection = document.getElementById("application");
        const successMessage = document.getElementById("successMessage");

        applicationSection.style.display = "none";
        successMessage.style.display = "block";
        form.reset();
        successMessage.scrollIntoView({ behavior: "smooth" });
    } catch (error) {
        document.getElementById("loader").style.display = "none";
        alert(error.message);
    }
});


