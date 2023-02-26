
let table_headers = ["Month", "Generated\nkWh", "Cash\nSavings"];
const table_data = {
    "month": ["Jan", "Feb", "Mar"],
    "gen": ["123", "321", "213"],
    "sav": ["100", "200", "300"]
};


function generateTableHead(table, data) {
  let thead = table.createTHead();
  let row = thead.insertRow();
  for (let i = 0; i < table_headers.length; i++) {
    let th = document.createElement("th");
    let text = document.createTextNode(table_headers[i]);
    th.appendChild(text);
    row.appendChild(th);
  }
}

function generateTable(table, data) {
  const rows = data["month"].length;
  const keys = Object.keys(data);

  for (let i = 0; i < rows; i++) {
    let row = table.insertRow();
    for (key of keys) {
      let cell = row.insertCell();
      let text = document.createTextNode(data[key][i]);
      cell.appendChild(text);
    }
  }
}


let table = document.querySelector("table");
generateTableHead(table, table_headers);
generateTable(table, table_data);
