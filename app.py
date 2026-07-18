function doGet(e) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("App-Daten");
  
  // --- FALL 1: DATEN LESEN ---
  if (e.parameter.action === "read") {
    var data = sheet.getDataRange().getValues();
    var headers = data[0];
    var jsonArray = [];
    
    for (var i = 1; i < data.length; i++) {
      var row = data[i];
      var record = {};
      
      // Liest alle Spalten dynamisch aus, damit kein Deck verloren geht
      for (var j = 0; j < headers.length; j++) {
        var headerName = headers[j].toString().trim();
        if (headerName !== "") {
          record[headerName] = row[j];
        }
      }
      jsonArray.push(record);
    }
    
    return ContentService.createTextOutput(JSON.stringify(jsonArray))
      .setMimeType(ContentService.MimeType.JSON);
  }
  
  // --- FALL 2: DATEN SCHREIBEN ---
  var name = e.parameter.name;
  var deck = parseInt(e.parameter.deck);
  
  if (name && deck && e.parameter.werte) {
    var werte = e.parameter.werte.split(",");
    var data = sheet.getDataRange().getValues();
    var rowIndex = -1;
    
    for (var i = 0; i < data.length; i++) {
      if (data[i][0].toString().trim() == name.trim()) {
        rowIndex = i + 1;
        break;
      }
    }
    
    if (rowIndex != -1) {
      var startCol = 2 + (deck - 1) * 9;
      var rowValues = [werte.map(Number)];
      sheet.getRange(rowIndex, startCol, 1, 9).setValues(rowValues);
      return ContentService.createTextOutput("Erfolg");
    }
    return ContentService.createTextOutput("Spieler nicht gefunden");
  }
  
  return ContentService.createTextOutput("Ungültige Anfrage");
}
