import { useState } from "react";
import { useAuth } from "../../hooks/useAuth";
import { useNavigate } from "react-router-dom";

export default function LoginPage() {
  const { login, error, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username || !password) return;
    setSubmitting(true);
    const ok = await login(username, password);
    setSubmitting(false);
    if (ok) navigate("/dashboard", { replace: true });
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background:
          "radial-gradient(ellipse at 50% 0%, rgba(99,102,241,0.08) 0%, transparent 60%), var(--bg-primary)",
      }}
    >
      <div
        style={{
          width: 380,
          padding: "2rem",
          background: "var(--bg-surface)",
          border: "1px solid var(--border-color)",
          borderRadius: "var(--radius)",
          backdropFilter: "blur(12px)",
        }}
      >
        <div
          style={{
            textAlign: "center",
            marginBottom: "1.5rem",
          }}
        >
          <h1
            style={{
              fontSize: "1.5rem",
              fontWeight: 700,
              color: "var(--accent)",
              letterSpacing: "-0.02em",
            }}
          >
            CrowdSense AI
          </h1>
          <p style={{ fontSize: "0.8125rem", color: "var(--text-muted)", marginTop: 4 }}>
            Sign in to the dashboard
          </p>
        </div>

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          <div>
            <label
              style={{
                display: "block",
                fontSize: "0.75rem",
                color: "var(--text-muted)",
                marginBottom: 4,
                fontWeight: 500,
              }}
            >
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{
                width: "100%",
                padding: "10px 12px",
                borderRadius: 8,
                border: "1px solid var(--border-color)",
                background: "rgba(255,255,255,0.03)",
                color: "var(--text-primary)",
                fontSize: "0.875rem",
                outline: "none",
              }}
              placeholder="Enter username"
            />
          </div>

          <div>
            <label
              style={{
                display: "block",
                fontSize: "0.75rem",
                color: "var(--text-muted)",
                marginBottom: 4,
                fontWeight: 500,
              }}
            >
              Password
            </label>
            <div style={{ position: "relative" }}>
              <input
                type={showPw ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={{
                  width: "100%",
                  padding: "10px 12px",
                  paddingRight: 40,
                  borderRadius: 8,
                  border: "1px solid var(--border-color)",
                  background: "rgba(255,255,255,0.03)",
                  color: "var(--text-primary)",
                  fontSize: "0.875rem",
                  outline: "none",
                }}
                placeholder="Enter password"
              />
              <button
                type="button"
                onClick={() => setShowPw(!showPw)}
                style={{
                  position: "absolute",
                  right: 8,
                  top: "50%",
                  transform: "translateY(-50%)",
                  background: "none",
                  border: "none",
                  color: "var(--text-muted)",
                  fontSize: "0.75rem",
                }}
              >
                {showPw ? "Hide" : "Show"}
              </button>
            </div>
          </div>

          {error && (
            <div
              style={{
                fontSize: "0.8125rem",
                color: "var(--critical)",
                padding: "6px 10px",
                borderRadius: 6,
                background: "rgba(239,68,68,0.08)",
              }}
            >
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={submitting || !username || !password}
            style={{
              padding: "10px",
              borderRadius: 8,
              border: "none",
              background: submitting
                ? "rgba(99,102,241,0.5)"
                : "var(--accent)",
              color: "#fff",
              fontSize: "0.875rem",
              fontWeight: 600,
              cursor: submitting ? "not-allowed" : "pointer",
              transition: "var(--transition)",
              marginTop: 4,
            }}
            onMouseEnter={(e) => {
              if (!submitting) e.target.style.background = "var(--accent-hover)";
            }}
            onMouseLeave={(e) => {
              if (!submitting) e.target.style.background = "var(--accent)";
            }}
          >
            {submitting ? "Signing in..." : "Sign In"}
          </button>
        </form>
      </div>
    </div>
  );
}
