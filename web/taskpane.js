Office.onReady(() => {
    document.getElementById("cleanBtn").onclick = cleanActiveSheet;
});

async function cleanActiveSheet() {
    const status = document.getElementById("status");
    status.innerText = "Reading active sheet...";

    await Excel.run(async (context) => {
        const sheet = context.workbook.worksheets.getActiveWorksheet();
        const range = sheet.getUsedRange();
        range.load("values, columnCount, rowCount");
        await context.sync();

        // Convert sheet values to JSON
        const data = range.values.map(row => {
            let obj = {};
            for (let i = 0; i < row.length; i++) {
                obj["col" + i] = row[i];
            }
            return obj;
        });

        status.innerText = "Sending data to N.E.D. API...";

        // Send to backend
        const response = await fetch("https://ned-backend.onrender.com/clean", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ data })
        });

        const result = await response.json();

        // Write back cleaned data to sheet
        const cleanedValues = result.cleaned_data.map(obj => Object.values(obj));
        const cleanedRange = sheet.getRangeByIndexes(
            0,
            range.columnCount,
            range.rowCount,
            range.columnCount
        );
        cleanedRange.values = cleanedValues;

        await context.sync();
        status.innerText = "✅ Sheet cleaned!";
    });
}