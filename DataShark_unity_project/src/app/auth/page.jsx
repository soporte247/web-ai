"use client";

import { useState } from "react";

const DEFAULT_API = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";

export default function AuthPage() {
  const [mode, setMode] = useState("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const endpoint = mode === "login" ? "/auth/login" : "/auth/register";
      const res = await fetch(`${DEFAULT_API}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
      });

      const data = await res.json();

      if (!data.token) {
        setError("Credenciales inválidas o usuario ya existe");
        return;
      }

      localStorage.setItem("authToken", data.token);
      localStorage.setItem("userId", data.id);
      localStorage.setItem("username", data.username);

      window.location.href = "/";
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}>
      <form onSubmit={handleSubmit} style={{ width: 320, padding: "24px", background: "var(--panel)", borderRadius: "12px" }}>
        <h1 style={{ marginBottom: 24 }}>DataShark</h1>
        <p style={{ color: "var(--muted)", marginBottom: 20 }}>
          {mode === "login" ? "Ingresa a tu cuenta" : "Crea una nueva cuenta"}
        </p>

        <label>Usuario</label>
        <input value={username} onChange={(e) => setUsername(e.target.value)} required />

        <label>Contraseña</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />

        <button type="submit" disabled={loading}>
          {loading ? "Procesando..." : mode === "login" ? "Ingresar" : "Registrarse"}
        </button>

        {error && <p style={{ color: "#ef4444", fontSize: "0.85rem", marginTop: 12 }}>{error}</p>}

        <p style={{ marginTop: 20, textAlign: "center", color: "var(--muted)", fontSize: "0.85rem" }}>
          {mode === "login" ? "¿Sin cuenta? " : "¿Ya tienes cuenta? "}
          <button
            type="button"
            onClick={() => setMode(mode === "login" ? "register" : "login")}
            style={{ background: "none", border: "none", color: "var(--accent)", cursor: "pointer" }}
          >
            {mode === "login" ? "Regístrate" : "Inicia sesión"}
          </button>
        </p>
      </form>
    </div>
  );
}
