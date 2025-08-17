document.getElementById("getDataBtn").addEventListener("click", async () => {
  const resultDiv = document.getElementById("result");
  resultDiv.innerHTML = "⏳ Veriler alınıyor...";

  try {
    const response = await fetch("https://canli-analiz-1-59mx.onrender.com/"); // backend url
    if (!response.ok) {
      throw new Error("Sunucuya bağlanılamadı");
    }
    const data = await response.text();
    resultDiv.innerHTML = `<pre>${data}</pre>`;
  } catch (error) {
    resultDiv.innerHTML = `❌ Hata: ${error.message}`;
  }
});
