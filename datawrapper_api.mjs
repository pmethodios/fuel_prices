// datawrapper_api.mjs
import fetch from "node-fetch";   // ES module import
import { writeFile } from "fs/promises";

// -------------------------
// CONFIG
// -------------------------
const apiToken = "EuSaJuOEnX8DaEhf8zA3mdr41PO6McqTyf4ogGIsZ2Q8bdameEzO7GarU9BfH8Sc";  // Replace with your Datawrapper API token

// List of charts to export
const charts = [
  { id: "NIIJ5", filename: "chart1.png" },
  // Add more charts as needed
];

// -------------------------
// FUNCTION TO EXPORT PNG
// -------------------------
async function exportChartPNG(chartId, filename) {
  const url = `https://api.datawrapper.de/v3/charts/${chartId}/export/png`;

  const response = await fetch(url, {
    method: "GET",
    headers: {
      "Authorization": `Bearer ${apiToken}`
    }
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch chart ${chartId}: ${response.status} ${response.statusText}`);
  }

  const buffer = await response.arrayBuffer();
  await writeFile(filename, Buffer.from(buffer));
  console.log(`Saved ${filename}`);
}

// -------------------------
// MAIN SCRIPT
// -------------------------
async function main() {
  for (const chart of charts) {
    try {
      await exportChartPNG(chart.id, chart.filename);
    } catch (err) {
      console.error(err);
    }
  }
}

// Run the script
main();