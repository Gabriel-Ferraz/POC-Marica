"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { toast } from "sonner";
import AppLayout from "@/components/layout/AppLayout";
import { useAuth } from "@/hooks/useAuth";
import api from "@/lib/api";
import type { DLTNetwork } from "@/types";
import { Plus, Server, FileCode2, Key } from "lucide-react";

export default function DLTNetworksPage() {
  useAuth();
  const [networks, setNetworks] = useState<DLTNetwork[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", description: "" });

  const load = () => api.get("/api/dlt/networks").then((r) => setNetworks(r.data));
  useEffect(() => { load(); }, []);

  const create = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.post("/api/dlt/networks", form);
    toast.success("Rede criada");
    setShowForm(false);
    setForm({ name: "", description: "" });
    load();
  };

  return (
    <AppLayout>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Redes DLT</h1>
        <button onClick={() => setShowForm(true)} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700">
          <Plus size={16} /> Nova Rede
        </button>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <form onSubmit={create} className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl space-y-4">
            <h2 className="font-semibold text-lg">Nova Rede DLT</h2>
            <input placeholder="Nome da rede" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required className="w-full border rounded-lg px-3 py-2 text-sm" />
            <textarea placeholder="Descrição" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="w-full border rounded-lg px-3 py-2 text-sm" rows={2} />
            <div className="flex gap-3 justify-end">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-sm border rounded-lg">Cancelar</button>
              <button type="submit" className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg">Criar</button>
            </div>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {networks.map((net) => (
          <div key={net.id} className="bg-white border border-slate-200 rounded-xl p-5">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="font-semibold text-slate-900">{net.name}</h3>
                {net.description && <p className="text-sm text-slate-500 mt-1">{net.description}</p>}
              </div>
              <span className={`text-xs px-2 py-0.5 rounded-full ${net.is_active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>{net.is_active ? "Ativo" : "Inativo"}</span>
            </div>
            <div className="flex gap-2 flex-wrap">
              <Link href={`/dlt/contracts?network=${net.id}`} className="flex items-center gap-1 text-xs bg-purple-50 text-purple-700 border border-purple-200 px-3 py-1.5 rounded-lg hover:bg-purple-100">
                <FileCode2 size={12} /> Contratos
              </Link>
              <Link href={`/api-keys?network=${net.id}`} className="flex items-center gap-1 text-xs bg-slate-50 text-slate-700 border border-slate-200 px-3 py-1.5 rounded-lg hover:bg-slate-100">
                <Key size={12} /> API Keys
              </Link>
              <Link href={`/dlt/records?network=${net.id}`} className="flex items-center gap-1 text-xs bg-blue-50 text-blue-700 border border-blue-200 px-3 py-1.5 rounded-lg hover:bg-blue-100">
                <Server size={12} /> Registros
              </Link>
            </div>
          </div>
        ))}
        {networks.length === 0 && <div className="text-slate-400 text-center py-16 col-span-2">Nenhuma rede DLT cadastrada.</div>}
      </div>
    </AppLayout>
  );
}
