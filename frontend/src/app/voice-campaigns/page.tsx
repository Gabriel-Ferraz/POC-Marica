"use client";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import AppLayout from "@/components/layout/AppLayout";
import { useAuth } from "@/hooks/useAuth";
import api from "@/lib/api";
import type { VoiceCampaign } from "@/types";
import { Plus, Megaphone } from "lucide-react";

export default function VoiceCampaignsPage() {
  useAuth();
  const [campaigns, setCampaigns] = useState<VoiceCampaign[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", description: "", ideal_hours: "9,10,11,14,15,16" });

  const load = () => api.get("/api/voice/campaigns").then((r) => setCampaigns(r.data));
  useEffect(() => { load(); }, []);

  const create = async (e: React.FormEvent) => {
    e.preventDefault();
    const hours = form.ideal_hours.split(",").map(Number).filter((n) => !isNaN(n));
    await api.post("/api/voice/campaigns", { name: form.name, description: form.description, ideal_hours: hours });
    toast.success("Campanha criada");
    setShowForm(false);
    load();
  };

  const statusColors: Record<string, string> = {
    draft: "bg-slate-100 text-slate-600",
    active: "bg-green-100 text-green-700",
    paused: "bg-yellow-100 text-yellow-700",
    completed: "bg-blue-100 text-blue-700",
  };

  return (
    <AppLayout>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Campanhas de Voz Ativas</h1>
        <button onClick={() => setShowForm(true)} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700">
          <Plus size={16} /> Nova Campanha
        </button>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <form onSubmit={create} className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl space-y-4">
            <h2 className="font-semibold text-lg">Nova Campanha</h2>
            <input placeholder="Nome da campanha" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required className="w-full border rounded-lg px-3 py-2 text-sm" />
            <textarea placeholder="Descrição / roteiro inicial" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="w-full border rounded-lg px-3 py-2 text-sm" rows={3} />
            <div>
              <label className="text-xs text-slate-500">Horários ideais (horas, separadas por vírgula)</label>
              <input value={form.ideal_hours} onChange={(e) => setForm({ ...form, ideal_hours: e.target.value })} className="w-full border rounded-lg px-3 py-2 text-sm" placeholder="9,10,14,15" />
            </div>
            <div className="flex gap-3 justify-end">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-sm border rounded-lg">Cancelar</button>
              <button type="submit" className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg">Criar</button>
            </div>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {campaigns.map((c) => (
          <div key={c.id} className="bg-white border border-slate-200 rounded-xl p-5">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <Megaphone size={16} className="text-blue-600" />
                <h3 className="font-semibold text-slate-900">{c.name}</h3>
              </div>
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${statusColors[c.status] || "bg-slate-100 text-slate-600"}`}>{c.status}</span>
            </div>
            {c.description && <p className="text-sm text-slate-500 mb-3">{c.description}</p>}
            {c.ideal_hours.length > 0 && (
              <p className="text-xs text-slate-400">Horários: {c.ideal_hours.map((h) => `${h}h`).join(", ")}</p>
            )}
          </div>
        ))}
        {campaigns.length === 0 && <div className="text-slate-400 text-center py-16 col-span-3">Nenhuma campanha cadastrada.</div>}
      </div>
    </AppLayout>
  );
}
