async function loadLiveMatches() {
  try {
    const res = await fetch("https://canli-analiz-1-59mx.onrender.com/live-stats");
    const data = await res.json();

    const container = document.getElementById("matches");
    container.innerHTML = "";

    if (!data.response || data.response.length === 0) {
      container.innerHTML = "<p>Şu anda canlı maç bulunmuyor.</p>";
      return;
    }

    data.response.forEach(match => {
      const div = document.createElement("div");
      div.className = "match-card";

      div.innerHTML = `
        <h3>${match.teams.home.name} vs ${match.teams.away.name}</h3>
        <p><strong>Lig:</strong> ${match.league.name} (${match.league.country})</p>
        <p><strong>Durum:</strong> ${match.fixture.status.long} (${match.fixture.status.elapsed}' dk)</p>
        <p><strong>Skor:</strong> ${match.goals.home ?? 0} - ${match.goals.away ?? 0}</p>
      `;

      container.appendChild(div);
    });
  } catch (err) {
    console.error("API hatası:", err);
    document.getElementById("matches").innerHTML = "<p>Veri yüklenirken hata oluştu.</p>";
  }
}

loadLiveMatches();
setInterval(loadLiveMatches, 30000); // her 30 saniyede yenile
