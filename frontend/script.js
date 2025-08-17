const BACKEND_URL = "https://canli-analiz-1-59mx.onrender.com/live-matches";
const statusEl = document.getElementById("status");
const listEl = document.getElementById("list");
const refreshBtn = document.getElementById("refreshBtn");

async function loadMatches() {
  statusEl.textContent = "⏳ Veriler alınıyor...";
  try {
    const res = await fetch(BACKEND_URL);
    const payload = await res.json();

    // bizim backend: { status_code, ok, host, url, body }
    if (!payload.ok || !payload.body) {
      statusEl.textContent = `⚠️ Beklenmedik yanıt (code: ${payload.status_code})`;
      console.log(payload);
      listEl.innerHTML = "";
      return;
    }

    const items = Array.isArray(payload.body) ? payload.body : [];
    statusEl.textContent = `✅ Toplam ${items.length} kayıt`;

    if (items.length === 0) {
      listEl.innerHTML = "<p>Şu an listelenecek canlı içerik bulunamadı.</p>";
      return;
    }

    // İlk 20 kaydı render edelim
    listEl.innerHTML = items.slice(0, 20).map(item => {
      const title = item.title || "Maç";
      const comp = item.competition?.name || "";
      const dt = item.date ? new Date(item.date).toLocaleString() : "";
      const thumb = item.thumbnail || "";
      const pageUrl = item.url || "#";
      const embedHtml = item.embed || "";

      return `
        <div class="card">
          <h3>${title}</h3>
          ${comp ? `<div class="meta">🏆 ${comp}</div>` : ""}
          ${dt ? `<div class="meta">🕒 ${dt}</div>` : ""}
          ${thumb ? `<img class="thumb" src="${thumb}" alt="${title}">` : ""}
          <div style="margin:8px 0;">
            <a class="btn" href="${pageUrl}" target="_blank" rel="noopener">Kaynağa Git</a>
          </div>
          ${embedHtml ? `<details style="margin-top:8px;"><summary>▶️ Yayını Göster</summary>${embedHtml}</details>` : ""}
        </div>
      `;
    }).join("");

  } catch (err) {
    statusEl.textContent = "❌ Bağlantı hatası: " + err.message;
    listEl.innerHTML = "";
  }
}

// buton ve otomatik yenileme
refreshBtn.addEventListener("click", loadMatches);
document.addEventListener("DOMContentLoaded", () => {
  loadMatches();
  setInterval(loadMatches, 60 * 1000); // 60 sn'de bir yenile
});
