function fillOutDefaults() {
    const months = [
        "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"
    ];
    document.getElementById(`name`).value = "Default";
    document.getElementById(`address`).value = "93101";

    for (let i = 0; i < months.length; i++) {
        document.getElementById(`energy${months[i]}`).value = 150;
        document.getElementById(`cost${months[i]}`).value = 125;
    }
}