"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { toast } from "sonner";
import AppLayout from "@/components/layout/AppLayout";
import { useAuth } from "@/hooks/useAuth";
import api from "@/lib/api";
import type { Workflow } from "@/types";
import { Plus, Settings, Kanban } from "lucide-react";

export default function WorkflowsPage() {
  useAuth();
  const [items, setItems] = useState<Workflow[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", description: "" });

  const load = () => api.get("/api/workflows").then((r) => setItems(r.data));
  useEffect(() => { load(); }, []);

  const create = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.post("/api/workflows", form);
    toast.success("Fluxo criado");
    setShowForm(false);
    setForm({ name: "", description: "" });
    load();
  };

  return (
    <AppLayout>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Fluxos de Processo</h1>
        <button onClick={() => setShowForm(true)} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700">
          <Plus size={16} /> Novo Fluxo
        </button>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <form onSubmit={create} className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl space-y-4">
            <h2 className="font-semibold text-lg">Novo Fluxo</h2>
            <input placeholder="Nome do fluxo" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required className="w-full border rounded-lg px-3 py-2 text-sm" />
            <textarea placeholder="Descrição" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="w-full border rounded-lg px-3 py-2 text-sm" rows={3} />
            <div className="flex gap-3 justify-end">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-sm border rounded-lg">Cancelar</button>
              <button type="submit" className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg">Criar</button>
            </div>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {items.map((wf) => (
          <div key={wf.id} className="bg-white rounded-xl border border-slate-200 p-5">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="font-semibold text-slate-900">{wf.name}</h3>
                {wf.description && <p className="text-sm text-slate-500 mt-1 line-clamp-2">{wf.description}</p>}
              </div>
              <span className={`text-xs px-2 py-0.5 rounded-full ${wf.is_active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>{wf.is_active ? "Ativo" : "Inativo"}</span>
            </div>
            <div className="flex gap-2 mt-4">
              <Link href={`/workflows/${wf.id}/steps`} className="flex items-center gap-1 text-xs bg-slate-100 hover:bg-slate-200 px-3 py-1.5 rounded-lg transition-colors">
                <Settings size={12} /> Etapas
              </Link>
              <Link href={`/workflows/${wf.id}/kanban`} className="flex items-center gap-1 text-xs bg-blue-50 hover:bg-blue-100 text-blue-700 px-3 py-1.5 rounded-lg transition-colors">
                <Kanban size={12} /> Kanban
              </Link>
            </div>
          </div>
        ))}
      </div>
    </AppLayout>
  );
}
