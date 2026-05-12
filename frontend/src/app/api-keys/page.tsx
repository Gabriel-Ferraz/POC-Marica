"use client";
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { toast } from "sonner";
import AppLayout from "@/components/layout/AppLayout";
import { useAuth } from "@/hooks/useAuth";
import api from "@/lib/api";
import type { DLTCredential, DLTNetwork } from "@/types";
import { Plus, Copy, Eye, EyeOff } from "lucide-react";

export default function ApiKeysPage() {
  useAuth();
  const searchParams = useSearchParams();
  const [networks, setNetworks] = useState<DLTNetwork[]>([]);
  const [selectedNetwork, setSelectedNetwork] = useState(searchParams.get("network") || "");
  const [credentials, setCredentials] = useState<DLTCredential[]>([]);
  const [newSecret, setNewSecret] = useState<{ name: string; access_key: string; secret_key: string } | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", allowed_routes: "/api/dlt/records" });
  const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({});

  useEffect(() => {
    api.get("/api/dlt/networks").then((r) => {
      setNetworks(r.data);
      if (!selectedNetwork && r.data[0]) setSelectedNetwork(r.data[0].id);
    });
  }, []);

  useEffect(() => {
    if (selectedNetwork) api.get(`/api/dlt/networks/${selectedNetwork}/credentials`).then((r) => setCredentials(r.data));
  }, [selectedNetwork]);

  const create = async (e: React.FormEvent) => {
    e.preventDefault();
    const routes = form.allowed_routes.split(",").map((s) => s.trim()).filter(Boolean);
    const { data } = await api.post(`/api/dlt/networks/${selectedNetwork}/credentials`, { name: form.name, allowed_routes: routes });
    setNewSecret({ name: data.name, access_key: data.access_key, secret_key: data.secret_key });
    setShowForm(false);
    api.get(`/api/dlt/networks/${selectedNetwork}/credentials`).then((r) => setCredentials(r.data));
  };

  const copy = (text: string) => { navigator.clipboard.writeText(text); toast.success("Copiado!"); };

  return (
    <AppLayout>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-900">API Keys (accessKey / secretKey)</h1>
        <button onClick={() => setShowForm(true)} disabled={!selectedNetwork} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 disabled:opacity-40">
          <Plus size={16} /> Gerar Chaves
        </button>
      </div>

      <div className="mb-6">
        <select value={selectedNetwork} onChange={(e) => setSelectedNetwork(e.target.value)} className="border rounded-lg px-3 py-2 text-sm">
          {networks.map((n) => <option key={n.id} value={n.id}>{n.name}</option>)}
        </select>
      </div>

      {newSecret && (
        <div className="bg-green-50 border border-green-300 rounded-xl p-5 mb-6">
          <h3 className="font-semibold text-green-900 mb-3">⚠️ Guarde agora — a secretKey não será exibida novamente</h3>
          <div className="space-y-2 font-mono text-sm">
            <div className="flex items-center gap-2"><span className="text-green-700 font-semibold w-24">accessKey:</span><span className="text-green-900">{newSecret.access_key}</span><button onClick={() => copy(newSecret.access_key)}><Copy size={14} /></button></div>
            <div className="flex items-center gap-2"><span className="text-green-700 font-semibold w-24">secretKey:</span><span className="text-green-900">{newSecret.secret_key}</span><button onClick={() => copy(newSecret.secret_key)}><Copy size={14} /></button></div>
          </div>
          <div className="mt-3 text-xs text-slate-600 bg-white border rounded p-3">
            <strong>Uso via HTTP:</strong><br />
            <code>X-Access-Key: {newSecret.access_key}</code><br />
            <code>X-Secret-Key: {newSecret.secret_key}</code>
          </div>
          <button onClick={() => setNewSecret(null)} className="mt-3 text-xs text-slate-500 hover:underline">Fechar</button>
        </div>
      )}

      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <form onSubmit={create} className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl space-y-4">
            <h2 className="font-semibold text-lg">Gerar API Keys</h2>
            <input placeholder="Nome da credencial" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required className="w-full border rounded-lg px-3 py-2 text-sm" />
            <div>
              <label className="text-xs text-slate-500">Rotas permitidas (separadas por vírgula)</label>
              <input value={form.allowed_routes} onChange={(e) => setForm({ ...form, allowed_routes: e.target.value })} className="w-full border rounded-lg px-3 py-2 text-sm" />
            </div>
            <div className="flex gap-3 justify-end">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-sm border rounded-lg">Cancelar</button>
              <button type="submit" className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg">Gerar</button>
            </div>
          </form>
        </div>
      )}

      <div className="space-y-3">
        {credentials.map((cred) => (
          <div key={cred.id} className="bg-white border border-slate-200 rounded-xl p-4 flex items-center justify-between">
            <div>
              <p className="font-semibold text-sm">{cred.name}</p>
              <p className="font-mono text-xs text-slate-500 mt-1">Access: {cred.access_key}</p>
              <p className="text-xs text-slate-400 mt-0.5">Rotas: {cred.allowed_routes.join(", ") || "todas"}</p>
            </div>
            <div className="flex items-center gap-2">
              <span className={`text-xs px-2 py-0.5 rounded-full ${cred.is_active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>{cred.is_active ? "Ativa" : "Inativa"}</span>
              <button onClick={() => copy(cred.access_key)} className="text-slate-400 hover:text-slate-600"><Copy size={14} /></button>
            </div>
          </div>
        ))}
        {credentials.length === 0 && <div className="text-slate-400 text-center py-12">Nenhuma credencial cadastrada.</div>}
      </div>
    </AppLayout>
  );
}
