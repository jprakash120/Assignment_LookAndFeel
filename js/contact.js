function openPopup() {
    document.getElementById("popup").style.display = "block";
}

function closePopup() {
    document.getElementById("popup").style.display = "none";
}


function closeConfirmationPopup() {
    document.getElementById("confirmationPopup").style.display = "none";
}


function submitForm() {

    
    closePopup();

    
    document.getElementById("confirmationPopup").style.display = "block";

    setTimeout(closeConfirmationPopup, 2000);

    
    clearForm();
}

function clearForm() {
    document.getElementById("contactForm").reset();
}