function fillOutDefaults() {
    // Function to fill out default values in main input form

    // Get switch value to know whether to fill out or clear form
    const do_switch = document.getElementById(`fill-out-def-switch`).value
    // Define array of months for getting monthly ID's
    const months = [
        "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"
    ];
    if (do_switch == 0) {
        // Fill out main 2 inputs: Name & Address
        document.getElementById(`name`).value = "Default";
        document.getElementById(`address`).value = "92024";
        // Fill out monthly values for Cost & Energy
        for (let i = 0; i < months.length; i++) {
            document.getElementById(`energy${months[i]}`).value = 150;
            document.getElementById(`cost${months[i]}`).value = 125;
        }
        document.getElementById(`fill-out-def-switch`).value = "1"
    } else {
            // Fill out main 2 inputs: Name & Address
        document.getElementById(`name`).value = null;
        document.getElementById(`address`).value = null;
        // Fill out monthly values for Cost & Energy
        for (let i = 0; i < months.length; i++) {
            document.getElementById(`energy${months[i]}`).value = null;
            document.getElementById(`cost${months[i]}`).value = null;
        }
        document.getElementById(`fill-out-def-switch`).value = "0"
    }
}