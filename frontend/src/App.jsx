import { useEffect, useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell, Legend
} from "recharts";

function App() {
  const [matches, setMatches] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const res = await fetch("http://localhost:8000/live"); // burayı sonra Render linkinle değiştireceğiz
      const data = await res.json();
      setMatches(data.matches);
    };

    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const COLORS = ["#22c55e", "#3b82f6"];

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h1 className="text-2xl font-bold mb-4">⚽ Canlı Maç Analiz Paneli</h1>
      <div className="grid gap-6">
        {matches.map((m, idx) => (
          <div key={idx} className="p-4 rounded-2xl shadow bg-white">
            <h2 className="font-semibold text-lg">
              {m.home} vs {m.away} ({m.minute}’)
            </h2>

            <p>Gol İhtimali: <span className={m.analysis.gol_ihtimali > 70 ? "text-green-600 font-bold" : "text-gray-700"}>%{m.analysis.gol_ihtimali}</span></p>
            <p>Korner İhtimali: <span className={m.analysis.korner_ihtimali > 60 ? "text-blue-600 font-bold" : "text-gray-700"}>%{m.analysis.korner_ihtimali}</span></p>

            {/* Momentum Grafiği */}
            <div className="mt-4">
              <h3 className="font-medium">Atak Momentumu</h3>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={m.analysis.momentum_graph}>
                  <XAxis dataKey="minute" hide />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Line type="monotone" dataKey="home" stroke="#22c55e" strokeWidth={2} />
                  <Line type="monotone" dataKey="away" stroke="#3b82f6" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Mini Grafikler */}
            <div className="grid grid-cols-2 gap-4 mt-6">
              <div>
                <h3 className="font-medium">Şutlar</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={[
                    { name: "Toplam Şut", home: m.analysis.shots.home, away: m.analysis.shots.away },
                    { name: "İsabetli Şut", home: m.analysis.shots_on_target.home, away: m.analysis.shots_on_target.away }
                  ]}>
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="home" fill="#22c55e" name={m.home} />
                    <Bar dataKey="away" fill="#3b82f6" name={m.away} />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div>
                <h3 className="font-medium">Topla Oynama</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={[
                        { name: m.home, value: m.analysis.possession.home },
                        { name: m.away, value: m.analysis.possession.away }
                      ]}
                      cx="50%"
                      cy="50%"
                      outerRadius={70}
                      dataKey="value"
                      label
                    >
                      {COLORS.map((color, index) => (
                        <Cell key={`cell-${index}`} fill={color} />
                      ))}
                    </Pie>
                    <Legend />
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            <p className="mt-4 text-sm text-gray-600">
              Kornerler: {m.analysis.corners.home} - {m.analysis.corners.away}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
