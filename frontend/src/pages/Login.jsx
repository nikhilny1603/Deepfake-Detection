import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      await login(email, password);
      toast.success("Welcome back!");
      nav("/dashboard");
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Login failed");
    } finally { setBusy(false); }
  };

  return (
    <div className="max-w-sm mx-auto glass p-6 mt-12">
      <h1 className="text-2xl font-bold mb-4">Sign in</h1>
      <form onSubmit={submit} className="space-y-3">
        <input className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2" placeholder="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2" placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        <button disabled={busy} className="btn-primary w-full">{busy ? "…" : "Sign in"}</button>
      </form>
      <p className="text-sm text-white/60 mt-4">
        No account? <Link to="/register" className="text-indigo-300">Create one</Link>
      </p>
    </div>
  );
}
