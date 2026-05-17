import { useState } from "react";
import toast from "react-hot-toast";
import api from "../api/client";

export default function Contact() {
  const [form, setForm] = useState({ name: "", email: "", subject: "", message: "" });
  const [sending, setSending] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setSending(true);
    try {
      await api.post("/api/contact", form);
      toast.success("Message sent. We'll be in touch.");
      setForm({ name: "", email: "", subject: "", message: "" });
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Could not send message");
    } finally {
      setSending(false);
    }
  };

  const F = (k) => (
    <input
      value={form[k]}
      onChange={(e) => setForm({ ...form, [k]: e.target.value })}
      className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 outline-none focus:border-indigo-400"
      required
    />
  );

  return (
    <div className="max-w-xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Contact</h1>
      <form onSubmit={submit} className="glass p-6 space-y-4">
        <Field label="Name">{F("name")}</Field>
        <Field label="Email"><input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 outline-none focus:border-indigo-400" required /></Field>
        <Field label="Subject">{F("subject")}</Field>
        <Field label="Message">
          <textarea
            rows={5}
            value={form.message}
            onChange={(e) => setForm({ ...form, message: e.target.value })}
            className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 outline-none focus:border-indigo-400"
            required
          />
        </Field>
        <button disabled={sending} className="btn-primary w-full disabled:opacity-50">
          {sending ? "Sending…" : "Send message"}
        </button>
      </form>
    </div>
  );
}

function Field({ label, children }) {
  return (
    <label className="block">
      <span className="text-sm text-white/60 block mb-1">{label}</span>
      {children}
    </label>
  );
}
