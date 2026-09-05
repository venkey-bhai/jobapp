console.log("SEARCH JS FILE LOADED");

const searchName = document.getElementById("searchName");
const searchCandidateBtn = document.getElementById("searchCandidateBtn");

if (searchCandidateBtn) {

    searchCandidateBtn.addEventListener("click", async function () {

        console.log("SEARCH BUTTON CLICKED");

        const name = searchName.value.trim();
         console.log("Name entered:", name);

        if (name === "") {
            alert("Please enter candidate name.");
            return;
        }

        alert("Search button is working!");

        candidateListSection.style.display = "block";
        candidateListMessage.textContent = "Searching...";
        candidateTableBody.innerHTML = "";

        try {

            const url =
                ` https://jobapp-koib.onrender.com/students/search/${encodeURIComponent(name)}/`;

            console.log("Calling API:", url);

            const response = await fetch(url);

            console.log("Status:", response.status);

            if (!response.ok) {

                if (response.status === 404) {
                    throw new Error("Candidate not found.");
                }

                throw new Error("Search failed.");
            }

            const data = await response.json();

            console.log("API DATA:", data);

            if (!Array.isArray(data) || data.length === 0) {
                candidateListMessage.textContent =
                    "No candidate found.";
                return;
            }

            candidateListMessage.textContent = "";

            data.forEach((candidate) => {
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
                    <td>${candidate.applied_date || "-"}</td>
                    <td>${candidate.created_at || "-"}</td>
                    <td>
                    
                    </td>
                `;

                candidateTableBody.appendChild(row);
            });

        } catch (error) {

            console.error("ERROR:", error);

            candidateListMessage.textContent =
                error.message;
        }

    });

}

   
