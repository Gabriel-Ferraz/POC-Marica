"use client";
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { toast } from "sonner";
import AppLayout from "@/components/layout/AppLayout";
import { useAuth } from "@/hooks/useAuth";
import api from "@/lib/api";
import type { SmartContract, DLTNetwork } from "@/types";
import { Plus, Trash2 } from "lucide-react";

export default function ContractsPage() {
  useAuth();
  const searchParams = useSearchParams();
  const networkId = searchParams.get("network");
  const [networks, setNetworks] = useState<DLTNetwork[]>([]);
  const [contracts, setContracts] = useState<SmartContract[]>([]);
  const [selectedNetwork, setSelectedNetwork] = useState(networkId || "");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", description: "", fields: [{ name: "", field_type: "text", required: false }] });

  useEffect(() => {
    api.get("/api/dlt/networks").then((r) => { setNetworks(r.data); if (!selectedNetwork && r.data[0]) setSelectedNetwork(r.data[0].id); });
  }, []);

  useEffect(() => {
    if (selectedNetwork) api.get(`/api/dlt/networks/${selectedNetwork}/contracts`).then((r) => setContracts(r.data));
  }, [selectedNetwork]);

  const addField = () => setForm({ ...form, fields: [...form.fields, { name: "", field_type: "text", required: false }] });

  const create = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.post(`/api/dlt/networks/${selectedNetwork}/contracts`, form);
    toast.success("Contrato criado");
    setShowForm(false);
    api.get(`/api/dlt/networks/${selectedNetwork}/contracts`).then((r) => setContracts(r.data));
  };

  return (
    <AppLayout>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Contratos Inteligentes</h1>
        <button onClick={() => setShowForm(true)} disabled={!selectedNetwork} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 disabled:opacity-40">
          <Plus size={16} /> Novo Contrato
        </button>
      </div>

      <div className="mb-6">
        <label className="block text-sm font-medium text-slate-700 mb-1">Rede DLT</label>
        <select value={selectedNetwork} onChange={(e) => setSelectedNetwork(e.target.value)} className="border rounded-lg px-3 py-2 text-sm">
          {networks.map((n) => <option key={n.id} value={n.id}>{n.name}</option>)}
        </select>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <form onSubmit={create} className="bg-white rounded-xl p-6 w-full max-w-lg shadow-xl space-y-4 max-h-[90vh] overflow-y-auto">
            <h2 className="font-semibold text-lg">Novo Contrato Inteligente</h2>
            <input placeholder="Nome" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required className="w-full border rounded-lg px-3 py-2 text-sm" />
            <textarea placeholder="Descrição" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="w-full border rounded-lg px-3 py-2 text-sm" rows={2} />
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Campos</span>
                <button type="button" onClick={addField} className="text-xs text-blue-600 hover:underline">+ Campo</button>
              </div>
              {form.fields.map((f, i) => (
                <div key={i} className="flex gap-2 mb-2">
                  <input placeholder="Nome do campo" value={f.name} onChange={(e) => { const fds = [...form.fields]; fds[i].name = e.target.value; setForm({ ...form, fields: fds }); }} className="flex-1 border rounded-lg px-3 py-2 text-sm" />
                  <select value={f.field_type} onChange={(e) => { const fds = [...form.fields]; fds[i].field_type = e.target.value; setForm({ ...form, fields: fds }); }} className="border rounded-lg px-2 py-2 text-sm">
                    <option value="text">Texto</option>
                    <option value="number">Número</option>
                    <option value="boolean">Booleano</option>
                    <option value="date">Data</option>
                    <option value="time">Hora</option>
                  </select>
                </div>
              ))}
            </div>
            <div className="flex gap-3 justify-end">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-sm border rounded-lg">Cancelar</button>
              <button type="submit" className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg">Criar</button>
            </div>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {contracts.map((c) => (
          <div key={c.id} className="bg-white border border-slate-200 rounded-xl p-5">
            <h3 className="font-semibold text-slate-900">{c.name}</h3>
            {c.description && <p className="text-sm text-slate-500 mt-1">{c.description}</p>}
            <p className="text-xs text-slate-400 mt-3">ID: {c.id.slice(0, 8)}...</p>
          </div>
        ))}
        {contracts.length === 0 && <div className="text-slate-400 text-center py-16 col-span-2">Nenhum contrato nesta rede.</div>}
      </div>
    </AppLayout>
  );
}
