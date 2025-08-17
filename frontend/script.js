async function getMatchStats() {
  const matchId = document.getElementById("matchIdInput").value;
  if (!matchId) {
    alert("Lütfen bir maç ID giriniz!");
    return;
  }

  const response = await fetch(
    `https://canli-analiz-1-59mx.onrender.com/match-stats/${matchId}`
  );
  const data = await response.json();

  const resultsDiv = document.getElementById("results");
  resultsDiv.innerHTML = "";

  if (data.error) {
    resultsDiv.innerHTML = `<p>❌ Hata: ${data.error}</p>`;
  } else if (data.message) {
    resultsDiv.innerHTML = `<p>⚠️ ${data.message}</p>`;
  } else {
    resultsDiv.innerHTML = `
      <div class="match-card">
        <h2>${data.home_team} 🆚 ${data.away_team}</h2>
        <p><strong>Lig:</strong> ${data.league} (${data.country})</p>
        <p><strong>Durum:</strong> ${data.status}</p>
        <p><strong>Tarih:</strong> ${new Date(data.date).toLocaleString()}</p>
        <p><strong>Skor:</strong> ${data.goals.home} - ${data.goals.away}</p>
      </div>
    `;
  }
}
