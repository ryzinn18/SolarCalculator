function fillOutDefaults() {
    // Function to fill out default values in main input form

    // Get switch value to know whether to fill out or clear form
    const do_switch = document.getElementById(`fill-out-def-switch`).value
    // Define arrays for months and default values
    const months = [
        "January", "February", "March", "April", "May", "June", "July",
        "August", "September", "October", "November", "December"
    ];
    const cost = [
        155.8, 148.2, 128.4, 140.6, 140.6, 121,
        133.95, 135.85, 134.9, 133.38, 149.5, 148.2
    ];
    const consumption = [
        820, 780, 679, 740, 720, 730,
        705, 715, 710, 702, 662, 780
    ];
    if (do_switch == 0) {
        // Fill out main 2 inputs: Name & Address
        document.getElementById(`name`).value = "Default Dan";
        document.getElementById(`address`).value = "93101";
        // Fill out monthly values for Cost & Energy
        for (let i = 0; i < months.length; i++) {
            document.getElementById(`energy${months[i]}`).value = consumption[i];
            document.getElementById(`cost${months[i]}`).value = cost[i];
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