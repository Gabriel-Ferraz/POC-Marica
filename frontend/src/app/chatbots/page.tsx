"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { toast } from "sonner";
import AppLayout from "@/components/layout/AppLayout";
import { useAuth } from "@/hooks/useAuth";
import api from "@/lib/api";
import type { Chatbot } from "@/types";
import { Plus, MessageSquare } from "lucide-react";

export default function ChatbotsPage() {
  useAuth();
  const [bots, setBots] = useState<Chatbot[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", description: "" });

  const load = () => api.get("/api/chatbots").then((r) => setBots(r.data));
  useEffect(() => { load(); }, []);

  const create = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.post("/api/chatbots", form);
    toast.success("Chatbot criado");
    setShowForm(false);
    setForm({ name: "", description: "" });
    load();
  };

  return (
    <AppLayout>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Chatbots</h1>
        <div className="flex gap-2">
          <button onClick={() => setShowForm(true)} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700">
            <Plus size={16} /> Novo Chatbot
          </button>
          <Link href="/chat-demo" className="flex items-center gap-2 bg-purple-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-purple-700">
            <MessageSquare size={16} /> Demo NLP
          </Link>
        </div>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <form onSubmit={create} className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl space-y-4">
            <h2 className="font-semibold text-lg">Novo Chatbot</h2>
            <input placeholder="Nome" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required className="w-full border rounded-lg px-3 py-2 text-sm" />
            <textarea placeholder="Descrição" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="w-full border rounded-lg px-3 py-2 text-sm" rows={3} />
            <div className="flex gap-3 justify-end">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-sm border rounded-lg">Cancelar</button>
              <button type="submit" className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg">Criar</button>
            </div>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {bots.map((bot) => (
          <div key={bot.id} className="bg-white border border-slate-200 rounded-xl p-5 flex items-start gap-4">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
              <MessageSquare size={18} className="text-blue-600" />
            </div>
            <div className="flex-1">
              <div className="flex items-start justify-between">
                <h3 className="font-semibold text-slate-900">{bot.name}</h3>
                <span className={`text-xs px-2 py-0.5 rounded-full ${bot.is_active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>{bot.is_active ? "Ativo" : "Inativo"}</span>
              </div>
              {bot.description && <p className="text-sm text-slate-500 mt-1">{bot.description}</p>}
              <Link href="/chat-demo" className="mt-3 inline-block text-xs text-blue-600 hover:underline">Abrir no Demo →</Link>
            </div>
          </div>
        ))}
        {bots.length === 0 && <div className="text-slate-400 text-center py-16 col-span-3">Nenhum chatbot criado.</div>}
      </div>
    </AppLayout>
  );
}
