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


function toggleLoader() {
    // Temporarily display loader page after submitting input
    let status = document.getElementById('loading').style.display;
    if (status == "block") {
        document.getElementById('loading').style.display = "none";
    }
    else {
        document.getElementById('loading').style.display = "block";
    }
//    // Show the loader
//    document.getElementById('loading').style.display = "block";
//    // Remove loader after 12 seconds (request takes <= 12 seconds before timeout)
//    setTimeout(function() {
//        document.getElementById('loading').style.display = "none";
//    }, 12000);
}

function toggleLoaderOn() {
    // Temporarily display loader page after submitting input
    document.getElementById('loading').style.display = "block";
}

function toggleLoaderOff() {
    // Temporarily display loader page after submitting input
    document.getElementById('loading').style.display = "none";
}

function initialize() {
    // Organize all of the initialization of data

    // Toggle loader to on
    document.getElementById('loading').style.display = "block";

    // Lock the init form
    document.getElementById('def-switch').style.display = "none";
    document.getElementById('frm-init').disabled = true;
    document.getElementById('input-data-button').style.display = "none";
    document.getElementById('go-back-button').style.display = "block";

    // Define parameters entered in form
    const name = document.getElementById('name').value;
    const address = document.getElementById('address').value;
    const rating = document.getElementById('rating').value;
    const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    let energy = []
    let cost = []
    for (let i = 0; i < months.length; i++) {
        energy.push(document.getElementById(`energy${months[i]}`).value);
        cost.push(document.getElementById(`cost${months[i]}`).value);
    }

    // call /init-tool
    fetch(`/init-data/?name=${name}&address=${address}&rating=${rating}&energy=${energy}&cost=${cost}`)
    .then((res) => res.json())
    .then((data) => {
        if (data["status"]["status_code"] == 200) {
            document.getElementById('final-data').style.display = "block";

            document.getElementById('mod-quantity').value = data["mod_quantity"];
            document.getElementById('capacity').innerHTML = data["capacity"];
            document.getElementById('state').innerHTML = data["state"];
            document.getElementById('state-price').innerHTML = data["state_price"];
            document.getElementById('total-price').innerHTML = data["total_price"];
            document.getElementById('tax-credit').innerHTML = data["tax_credit"];
            document.getElementById('discount-price').innerHTML = data["discount_price"];
        }
        else {
            alert("Something went wrong.")
        }
    }).catch((e) => alert(`An error occurred: ${e}`));

    document.getElementById('loading').style.display = "none";
}

function returnToInit() {
    document.getElementById('final-data').style.display = "none";
    document.getElementById('def-switch').style.display = "block";
    document.getElementById('frm-init').disabled = false;
    document.getElementById('input-data-button').style.display = "block";
    //document.getElementById('go-back-button').style.display = "none";

}

function calculateArrayValues() {
    // Function to dynamically update estimate values based on quantity of solar modules

    // Obtain current values
    const quantity = document.getElementById('mod-quantity').value;
    const rating = Number(document.getElementById('rating').value);
    const price = parseFloat(document.getElementById('state-price').innerHTML);

    // Calculate new value
    const capacity = Math.round(quantity * rating * 100) / 100;
    const total_price = Math.round(capacity * price * 1000);
    const tax_credit = Math.round(total_price * 0.3);
    const discount_price = Math.round(total_price * 0.7);

    // Update new values
    document.getElementById('capacity').innerHTML = capacity;
    document.getElementById('total-price').innerHTML = total_price;
    document.getElementById('tax-credit').innerHTML = tax_credit;
    document.getElementById('discount-price').innerHTML = discount_price;
}

function getResults() {

}