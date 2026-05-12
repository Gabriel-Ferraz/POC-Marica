"use client";
import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/AppLayout";
import { useAuth } from "@/hooks/useAuth";
import api from "@/lib/api";
import type { DLTRecord } from "@/types";
import { Search } from "lucide-react";

export default function DLTRecordsPage() {
  useAuth();
  const [records, setRecords] = useState<DLTRecord[]>([]);
  const [search, setSearch] = useState("");
  const [found, setFound] = useState<DLTRecord | null>(null);

  useEffect(() => { api.get("/api/dlt/records").then((r) => setRecords(r.data)); }, []);

  const searchHash = async () => {
    if (!search) return;
    try {
      const { data } = await api.get(`/api/dlt/records/${search}`);
      setFound(data);
    } catch {
      setFound(null);
      alert("Hash não encontrado");
    }
  };

  return (
    <AppLayout>
      <h1 className="text-2xl font-bold text-slate-900 mb-6">Registros DLT</h1>

      <div className="flex gap-3 mb-6">
        <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Buscar por hash SHA-256..." className="flex-1 border rounded-lg px-4 py-2 text-sm" onKeyDown={(e) => e.key === "Enter" && searchHash()} />
        <button onClick={searchHash} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700">
          <Search size={16} /> Buscar
        </button>
      </div>

      {found && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
          <h3 className="font-semibold text-blue-900 mb-2">Registro encontrado</h3>
          <pre className="text-xs text-blue-800 overflow-x-auto">{JSON.stringify(found, null, 2)}</pre>
        </div>
      )}

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b">
            <tr>
              <th className="text-left px-4 py-3 text-slate-600 font-medium">Evento</th>
              <th className="text-left px-4 py-3 text-slate-600 font-medium">Hash</th>
              <th className="text-left px-4 py-3 text-slate-600 font-medium">Data/Hora</th>
            </tr>
          </thead>
          <tbody>
            {records.map((r) => (
              <tr key={r.id} className="border-b border-slate-100 hover:bg-slate-50">
                <td className="px-4 py-3">
                  <span className="bg-purple-100 text-purple-700 text-xs px-2 py-0.5 rounded-full font-medium">{r.event_type}</span>
                </td>
                <td className="px-4 py-3 font-mono text-xs text-slate-600">{r.record_hash.slice(0, 16)}...{r.record_hash.slice(-8)}</td>
                <td className="px-4 py-3 text-slate-500">{new Date(r.created_at).toLocaleString("pt-BR")}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {records.length === 0 && <div className="text-center py-12 text-slate-400">Nenhum registro DLT ainda.</div>}
      </div>
    </AppLayout>
  );
}
