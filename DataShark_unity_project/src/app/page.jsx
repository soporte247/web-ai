"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import WorldCanvas from "../components/WorldCanvas";

const DEFAULT_API = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";

export default function HomePage() {
  const [prompt, setPrompt] = useState("Ciudad costera futurista con clima cambiante");
  const [theme, setTheme] = useState("ciencia ficción");
  const [multiplayerMode, setMultiplayerMode] = useState("co-op");
  const [skillLevel, setSkillLevel] = useState("intermedio");
  const [enableArVr, setEnableArVr] = useState(true);
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [userId, setUserId] = useState("");
  const [username, setUsername] = useState("");

  useEffect(() => {
    const storedUserId = localStorage.getItem("userId");
    const storedUsername = localStorage.getItem("username");

    if (!storedUserId) {
      window.location.href = "/auth";
      return;
    }

    setUserId(storedUserId);
    setUsername(storedUsername || "Usuario");
  }, []);

  const handleGenerate = async () => {
    setLoading(true);
    setResponse(null);
    try {
      const res = await fetch(`${DEFAULT_API}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt,
          theme,
          platforms: ["Windows", "Mac", "Linux", "Android", "iOS"],
          enable_ar_vr: enableArVr,
          multiplayer_mode: multiplayerMode,
          player_skill_level: skillLevel
        })
      });

      const data = await res.json();
      setResponse(data);
    } catch (error) {
      setResponse({ error: String(error) });
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    window.location.href = "/auth";
  };

  return (
    <main>
      <aside>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
          <div className="header">
            <h1>DataShark</h1>
            <span className="badge">Web</span>
          </div>
        </div>

        <p style={{ color: "var(--muted)", fontSize: "0.85rem", marginBottom: 20 }}>Hola, {username}</p>

        <label>Prompt</label>
        <textarea value={prompt} onChange={(e) => setPrompt(e.target.value)} rows={4} />

        <label>Tema</label>
        <input value={theme} onChange={(e) => setTheme(e.target.value)} />

        <label>Multiplayer</label>
        <select value={multiplayerMode} onChange={(e) => setMultiplayerMode(e.target.value)}>
          <option value="co-op">Cooperativo</option>
          <option value="competitive">Competitivo</option>
        </select>

        <label>Nivel del jugador</label>
        <select value={skillLevel} onChange={(e) => setSkillLevel(e.target.value)}>
          <option value="principiante">Principiante</option>
          <option value="intermedio">Intermedio</option>
          <option value="avanzado">Avanzado</option>
        </select>

        <label>
          <input
            type="checkbox"
            checked={enableArVr}
            onChange={(e) => setEnableArVr(e.target.checked)}
          />
          Soporte AR/VR
        </label>

        <button onClick={handleGenerate} disabled={loading}>
          {loading ? "Generando..." : "Generar mundo"}
        </button>

        <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
          <Link href="/library" style={{ flex: 1, textAlign: "center", padding: "8px 12px", color: "var(--text)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, textDecoration: "none" }}>
            Mi biblioteca
          </Link>
          <button onClick={handleLogout} style={{ flex: 1, padding: "8px 12px", background: "#dc2626", color: "white" }}>
            Logout
          </button>
        </div>

        <div className="panel">
          <strong>Respuesta del backend</strong>
          <pre>{response ? JSON.stringify(response, null, 2) : "Sin respuesta todavía."}</pre>
        </div>
      </aside>
      <section>
        <h2>Vista 3D</h2>
        <WorldCanvas theme={theme} />
      </section>
    </main>
  );
}
