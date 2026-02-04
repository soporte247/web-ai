"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const DEFAULT_API = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";

export default function LibraryPage() {
  const [worlds, setWorlds] = useState([]);
  const [userId, setUserId] = useState("");
  const [username, setUsername] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedUserId = localStorage.getItem("userId");
    const storedUsername = localStorage.getItem("username");

    if (!storedUserId || !storedUsername) {
      window.location.href = "/auth";
      return;
    }

    setUserId(storedUserId);
    setUsername(storedUsername);
    loadWorlds(storedUserId);
  }, []);

  const loadWorlds = async (uid) => {
    try {
      const res = await fetch(`${DEFAULT_API}/worlds?user_id=${uid}`);
      const data = await res.json();
      setWorlds(data.worlds || []);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    window.location.href = "/auth";
  };

  return (
    <div style={{ padding: "24px", maxWidth: "900px", margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32 }}>
        <h1>Mis mundos</h1>
        <div style={{ display: "flex", gap: 12 }}>
          <Link href="/" style={{ color: "var(--accent)" }}>
            Crear mundo
          </Link>
          <button onClick={handleLogout} style={{ background: "#dc2626", color: "white", padding: "8px 16px", borderRadius: "6px" }}>
            Logout
          </button>
        </div>
      </div>

      {loading ? (
        <p>Cargando...</p>
      ) : worlds.length === 0 ? (
        <p style={{ color: "var(--muted)" }}>No tienes mundos guardados. <Link href="/" style={{ color: "var(--accent)" }}>Crea uno</Link></p>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 16 }}>
          {worlds.map((world) => (
            <div key={world.id} style={{ padding: 16, background: "var(--panel)", borderRadius: 12, border: "1px solid rgba(255,255,255,0.08)" }}>
              <h3>{world.summary}</h3>
              <p style={{ color: "var(--muted)", fontSize: "0.85rem", margin: "8px 0" }}>
                {new Date(world.created_at).toLocaleDateString()}
              </p>
              <Link href={`/?world=${world.id}`} style={{ color: "var(--accent)", textDecoration: "none" }}>
                Ver &rarr;
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
