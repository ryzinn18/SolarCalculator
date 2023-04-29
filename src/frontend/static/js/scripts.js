window.addEventListener('DOMContentLoaded', event => {

    // Navbar shrink function
    var navbarShrink = function () {
        const navbarCollapsible = document.body.querySelector('#mainNav');
        if (!navbarCollapsible) {
            return;
        }
        if (window.scrollY === 0) {
            navbarCollapsible.classList.remove('navbar-shrink')
        } else {
            navbarCollapsible.classList.add('navbar-shrink')
        }

    };

    // Shrink the navbar 
    navbarShrink();

    // Shrink the navbar when page is scrolled
    document.addEventListener('scroll', navbarShrink);

    // Activate Bootstrap scrollspy on the main nav element
    const mainNav = document.body.querySelector('#mainNav');
    if (mainNav) {
        new bootstrap.ScrollSpy(document.body, {
            target: '#mainNav',
            offset: 74,
        });
    };

    // Collapse responsive navbar when toggler is visible
    const navbarToggler = document.body.querySelector('.navbar-toggler');
    const responsiveNavItems = [].slice.call(
        document.querySelectorAll('#navbarResponsive .nav-link')
    );
    responsiveNavItems.map(function (responsiveNavItem) {
        responsiveNavItem.addEventListener('click', () => {
            if (window.getComputedStyle(navbarToggler).display !== 'none') {
                navbarToggler.click();
            }
        });
    });

    // Activate SimpleLightbox plugin for portfolio items
    new SimpleLightbox({
        elements: '#portfolio a.portfolio-box'
    });

});

function _toggleLoaderOn() {
    // Temporarily display loader page after submitting input
    document.getElementById('loading').style.display = "block";
}


function _toggleLoaderOff() {
    // Temporarily display loader page after submitting input
    document.getElementById('loading').style.display = "none";
}


function _getInitData() {
    // Get all of the data from the initial input form

    // Define initData object from input form values
    let initData = {
        username: document.getElementById('username').value,
        address: document.getElementById('address').value,
        rating: document.getElementById('rating').value,
        energy: [],
        cost: []
    };

    // Define months list for keying energy and cost values
    const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    // Iterate through months using months as part of key for cost and values figures
    for (let i = 0; i < months.length; i++) {
        initData.energy.push(document.getElementById(`energy${months[i]}`).value);
        initData.cost.push(document.getElementById(`cost${months[i]}`).value);
    };

    return initData;
}


function _getFinalData() {
    // Get necessary data from final form
    const finalData = {
        username: document.getElementById('username').value,
        time_stamp: document.getElementById('time-stamp').innerHTML,
        address: document.getElementById('address').value,
        mod_quantity: document.getElementById('mod-quantity').value,
        capacity: document.getElementById('capacity').innerHTML,
        rating: document.getElementById('rating').value,
    };

    return finalData;
}


function _lockInitForm() {
    // Locks the initial input form
    document.getElementById('def-switch').style.display = "none";
    document.getElementById('frm-init').disabled = true;
    document.getElementById('input-data-button').style.display = "none";
    document.getElementById('go-back-button').style.display = "block";
}


function _showFinalSection(init_data, solar_data) {
    // Calculate suggested figures for display
    const capacity = Math.round((init_data.energy_annual / solar_data.output_annual) * 100) / 100;
    const quantity = Math.round(capacity / init_data.rating) + 1;
    // Display final-data section
    document.getElementById('final-data').style.display = "block";
    // Fill out final-data section
    document.getElementById('time-stamp').innerHTML = init_data.time_stamp;
    document.getElementById('mod-quantity').value = quantity;
    document.getElementById('capacity').innerHTML = capacity;
}


function unlockInitForm() {
    // Unlocks the initial input form
    document.getElementById('final-data').style.display = "none";
    document.getElementById('def-switch').style.display = "block";
    document.getElementById('frm-init').disabled = false;
    document.getElementById('input-data-button').style.display = "block";
    //document.getElementById('go-back-button').style.display = "none";
}


function initialize() {
    // Organize all of the initialization of data

    // Toggle loader to on
    _toggleLoaderOn();
    // Lock the init form
    _lockInitForm();
    // Define values entered in form
    const initData = _getInitData();

    // First, call /validate
    // Define /validate args
    const init_parameters = `?username=${initData.username}&address=${initData.address}&rating=${initData.rating}&energy=${initData.energy}&cost=${initData.cost}`;
    // Fetch /validate
    fetch(`/inputs/validate/${init_parameters}`)
    .then((res_validate) => res_validate.json())
    .then((init_data) => {
        if (init_data.status.status_code == 200) {
            // If Validating data is successful, get init solar data
            // Define /get-solar args
            const solar_parameters = `?address=${init_data.address}&capacity=1`;
            // Fetch /get-solar
            return fetch(`/get-solar/${solar_parameters}`)
                .then((res_solar) => res_solar.json())
                .then((solar_data) => {
                    if (solar_data.status.status_code == 200) {
                        // If the /get-solar call is successful, display final section
                        _showFinalSection(init_data, solar_data);
                        _toggleLoaderOff();
                    } else {
                        // If the /get-solar call is unsuccessful, alert user
                        alert(`Error: ${solar_data.status.message}`);
                        _toggleLoaderOff();
                    }
                }).catch((e) => alert(`Error: ${e}`));
        } else {
            // If the /validate call is unsuccessful, alert user
            alert(`Error: ${init_data.status.message}`);
            _toggleLoaderOff();
        }
    }).catch((e) => alert(`Error: ${e}`));
}


function finalize() {
    // Organize getting the results data

    // Toggle loader to on
    _toggleLoaderOn();

    // Define
    //const initData = _getInitData();
    const finalData = _getFinalData();

    const solar_parameters = `?capacity=${finalData.capacity}&address=${finalData.address}`;
    fetch(`/get-solar/${solar_parameters}`)
    .then((res_solar) => res_solar.json())
    .then((solar_data) => {
        if (solar_data.status.status_code == 200) {
            // If the /get-solar call is successful, call /inputs/finalize/
            const final_parameters = `?username=${finalData.username}&time=${finalData.time_stamp}&capacity=${finalData.capacity}&rating=${finalData.rating}&monthly=${solar_data.output_monthly}&annual=${solar_data.output_annual}&state=${solar_data.state}`;
            return fetch(`/inputs/finalize/${final_parameters}`)
                .then((res_final) => res_final.json())
                .then((inputs) => {
                    if (inputs.status.status_code == 200) {
                        // If the /inputs/finalize/ call is successful, call /get-results
                        const results_parameters = `?username=${finalData.username}&time=${finalData.time_stamp}`
                        return fetch(`/results/${results_parameters}`)
                            .then((res) => res.json())
                            .then((results) => {
                                if (results.status.status_code == 200) {
                                    alert('GREAT SUCCESS');
                                    _toggleLoaderOff()
                                } else {
                                    alert('ALMOST GREAT SUCCESS');
                                    _toggleLoaderOff()
                                }
                            })
                    } else {
                        // If the /get-solar call is unsuccessful, alert user
                        alert(`Error1: ${solar_data.status.message}`);
                        _toggleLoaderOff();
                    }
                }).catch((e) => alert(`Error2: ${e}`));
        } else {
            // If the /get-solar call is unsuccessful, alert user
            alert(`Error3: ${solar_data.status.message}`);
            _toggleLoaderOff();
        }
        }).catch((e) => alert(`Error4: ${e}`));
}


function calculateCapacity() {
    // Function to dynamically update estimate values based on quantity of solar modules

    // Obtain current values
    const quantity = document.getElementById('mod-quantity').value;
    const rating = Number(document.getElementById('rating').value);

    // Calculate new value
    const capacity = Math.round(quantity * rating * 100) / 100;

    // Update new values
    document.getElementById('capacity').innerHTML = capacity;
}
