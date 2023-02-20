// define the callAPI function that takes a first name and last name as parameters
var callAPI = (name,address,mod_kwh,consumption_monthly,cost_monthly)=>{
    // instantiate a headers object
    var myHeaders = new Headers();
    // add content type header to object
    myHeaders.append("Content-Type", "application/json");
    // using built in JSON utility package turn object to string and store in a variable
    var raw = JSON.stringify({
        "type":"form",
        "form":{
            "name":name,
            "address":address,
            "mod_kwh":mod_kwh,
            "consumption_monthly":consumption_monthly,
            "cost_monthly":cost_monthly
        }
    });
    // create a JSON object with parameters for API call and store in a variable
    var requestOptions = {
        method: 'POST',
        headers: myHeaders,
        body: raw,
        redirect: 'follow'
    };
    // make API call with parameters and use promises to get response
    fetch("https://xbmv3pz3k7.execute-api.us-west-1.amazonaws.com/dev", requestOptions)
    .then(response => response.text())
    .then(result => alert(JSON.parse(result).uid))
    .catch(error => console.log('error', error));
}
