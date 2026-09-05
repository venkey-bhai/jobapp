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
            // FIX 1: Added trailing slash to avoid 307 redirects
            const response = await fetch("https://your-app-name.onrender.com/students");

            if (!response.ok) {
                throw new Error("Could not load candidates.");
            }

            // FIX 2: Parsed the response array directly (no .candidates wrapper property)
            const candidates = await response.json(); 

            if (!candidates || candidates.length === 0) {
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
                    <td>${candidate.gender || "-"}</td>
                    <td>
                        <button 
                            class="delete-btn" 
                            onclick="deleteCandidate('${candidate.id}', this)">
                            Delete
                        </button>
                    </td>
                `;

                candidateTableBody.appendChild(row);
            });

        } catch (error) {
            candidateListMessage.textContent = error.message;
        }
    });
}

if (form) {
    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const resumeInput = document.getElementById("resume");

        if (!resumeInput.files.length) {
            alert("Please select your resume.");
            return;
        }

        // Show your loader graphic before initiating network traffic
        const loader = document.getElementById("loader");
        if (loader) loader.style.display = "block";

        const formData = new FormData();
        formData.append("fullname", document.getElementById("fullname").value);
        formData.append("gender", document.getElementById("gender").value); // Enforced by backend forms
        formData.append("email", document.getElementById("email").value);
        formData.append("mobile", document.getElementById("mobile").value);
        formData.append("position", document.getElementById("position").value);
        formData.append("qualification", document.getElementById("qualification").value);
        formData.append("experience", document.getElementById("experience").value);
        formData.append("yearOfPassing", document.getElementById("yearOfPassing").value);
        formData.append("percentage", document.getElementById("percentage").value);
        formData.append("college", document.getElementById("college").value);
        formData.append("primarySkills", document.getElementById("primarySkills").value);
        formData.append("secondarySkills", document.getElementById("secondarySkills").value);
        formData.append("languagesKnown", document.getElementById("languagesKnown").value);
        formData.append("resume", resumeInput.files[0]);

        try {
            // FIX 3: Pointed to the exact upload URL defined in main.py
            const response = await fetch("https://your-app-name.onrender.com/students/upload_resume/", {
                method: "POST",
                body: formData,
            });

            const result = await response.json();
            if (loader) loader.style.display = "none";

            if (!response.ok) {
                throw new Error(result.detail || "Application could not be submitted.");
            }

            const applicationSection = document.getElementById("application");
            const successMessage = document.getElementById("successMessage");

            if (applicationSection) applicationSection.style.display = "none";
            if (successMessage) {
                successMessage.style.display = "block";
                successMessage.scrollIntoView({ behavior: "smooth" });
            }
            form.reset();
        } catch (error) {
            if (loader) loader.style.display = "none";
            alert(error.message);
        }
    });
}

// Function to call FastAPI Delete API and remove row from table
async function deleteCandidate(id, buttonElement) {
  if (!id || id === "undefined") {
    alert("Invalid Candidate ID");
    return;
  }

  // Ask for confirmation before deleting
  const confirmDelete = confirm("Are you sure you want to delete this candidate?");
  if (!confirmDelete) return;

  try {
    const response = await fetch(`https://your-app-name.onrender.com/students/${id}/`, {
      method: "DELETE",
    });

    if (!response.ok) {
      throw new Error("Failed to delete candidate.");
    }

    const data = await response.json();
    alert(data.message || "Deleted successfully!");

    // Remove the table row visually from the DOM
    const row = buttonElement.closest("tr");
    row.remove();

  } catch (error) {
    console.error("Delete Error:", error);
    alert(error.message);
  }
}
