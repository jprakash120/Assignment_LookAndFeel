document.addEventListener("DOMContentLoaded", () => {
    const emojis = document.querySelectorAll(".emoji");
    const emojiRatingInput = document.getElementById("emojiRating");
    const feedbackForm = document.getElementById("feedbackForm");
    const feedbackList = document.getElementById("feedbackList");
    const popupForm = document.getElementById("popupForm");
    const editFeedbackForm = document.getElementById("editFeedbackForm");
    const modifyButton = document.getElementById("modifyButton");
    const cancelButton = document.getElementById("cancelButton");

    let currentEditItem = null;

    emojis.forEach(emoji => {
        emoji.addEventListener("click", () => {
            const feedback = emoji.getAttribute("data-feedback");
            emojiRatingInput.value = feedback;

            // Optionally add a visual indication of the selected emoji
            emojis.forEach(e => e.style.transform = "scale(1)");
            emoji.style.transform = "scale(1.2)";
        });
    });

    feedbackForm.addEventListener("submit", (event) => {
        event.preventDefault();
        
        const formData = new FormData(feedbackForm);
        const name = formData.get("name");
        const email = formData.get("email");
        const comments = formData.get("comments");
        const emojiRating = formData.get("emojiRating");

        // Create a new feedback item
        const feedbackItem = document.createElement("div");
        feedbackItem.classList.add("feedback-item");

        feedbackItem.innerHTML = `
            <h3>${name}</h3>
            <p>Email: ${email}</p>
            <p>Comments: ${comments}</p>
            <p>Rating: ${emojiRating}</p>
            <button class="edit-button"><i class="fas fa-edit"></i>Edit</button>
            <button class="delete-button"><i class="fas fa-trash-alt"></i>Delete</button>
        `;

        feedbackList.appendChild(feedbackItem);

        // Reset the form
        feedbackForm.reset();
        emojiRatingInput.value = "";
        emojis.forEach(e => e.style.transform = "scale(1)");

        // Add event listeners for the new buttons
        feedbackItem.querySelector(".delete-button").addEventListener("click", () => {
            feedbackList.removeChild(feedbackItem);
        });

        feedbackItem.querySelector(".edit-button").addEventListener("click", () => {
            currentEditItem = feedbackItem;
            document.getElementById("editName").value = name;
            document.getElementById("editEmail").value = email;
            document.getElementById("editComments").value = comments;
            document.getElementById("editEmojiRating").value = emojiRating;
            popupForm.style.display = "block";
        });
    });

    modifyButton.addEventListener("click", () => {
        if (currentEditItem) {
            const editedName = document.getElementById("editName").value;
            const editedEmail = document.getElementById("editEmail").value;
            const editedComments = document.getElementById("editComments").value;
            const editedEmojiRating = document.getElementById("editEmojiRating").value;

            currentEditItem.querySelector("h3").textContent = editedName;
            currentEditItem.querySelector("p:nth-child(2)").textContent = `Email: ${editedEmail}`;
            currentEditItem.querySelector("p:nth-child(3)").textContent = `Comments: ${editedComments}`;
            currentEditItem.querySelector("p:nth-child(4)").textContent = `Rating: ${editedEmojiRating}`;

            popupForm.style.display = "none";
        }
    });

    cancelButton.addEventListener("click", () => {
        popupForm.style.display = "none";
    });
});
