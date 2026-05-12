"use client";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import AppLayout from "@/components/layout/AppLayout";
import { useAuth } from "@/hooks/useAuth";
import api from "@/lib/api";
import type { AutomationPackage, AutomationRun } from "@/types";
import { Plus, Play, Shield, Terminal, Loader2 } from "lucide-react";

export default function AutomationsPage() {
  useAuth();
  const [packages, setPackages] = useState<AutomationPackage[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [running, setRunning] = useState<string | null>(null);
  const [reviewing, setReviewing] = useState<string | null>(null);
  const [selectedPkg, setSelectedPkg] = useState<string | null>(null);
  const [logs, setLogs] = useState<{ level: string; message: string }[]>([]);
  const [securityResult, setSecurityResult] = useState<{ risk_level: string; issues: { pattern: string; severity: string; message: string }[] } | null>(null);
  const [form, setForm] = useState({ name: "", description: "", language: "python", source_code: "# Automação Python de exemplo\nprint('Iniciando automação...')\nfor i in range(3):\n    print(f'Passo {i+1} concluído')\nprint('Automação finalizada!')" });

  const load = () => api.get("/api/automations").then((r) => setPackages(r.data));
  useEffect(() => { load(); }, []);

  const create = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.post("/api/automations", form);
    toast.success("Automação criada");
    setShowForm(false);
    load();
  };

  const run = async (pkgId: string) => {
    setRunning(pkgId);
    setSelectedPkg(pkgId);
    setLogs([]);
    try {
      const { data } = await api.post(`/api/automations/${pkgId}/run`);
      const logsRes = await api.get(`/api/automations/runs/${data.id}/logs`);
      setLogs(logsRes.data);
      toast.success(`Execução ${data.status}`);
    } catch {
      toast.error("Erro na execução");
    } finally {
      setRunning(null);
    }
  };

  const securityReview = async (pkgId: string) => {
    setReviewing(pkgId);
    try {
      const { data } = await api.post(`/api/automations/${pkgId}/security-review`);
      setSecurityResult(data);
      toast.success("Validação de segurança concluída");
    } finally {
      setReviewing(null);
    }
  };

  const riskColors: Record<string, string> = {
    low: "bg-green-100 text-green-700",
    medium: "bg-yellow-100 text-yellow-700",
    high: "bg-red-100 text-red-700",
    unknown: "bg-slate-100 text-slate-600",
  };

  return (
    <AppLayout>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Motor de Automação</h1>
        <button onClick={() => setShowForm(true)} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700">
          <Plus size={16} /> Nova Automação
        </button>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <form onSubmit={create} className="bg-white rounded-xl p-6 w-full max-w-2xl shadow-xl space-y-4 max-h-[90vh] overflow-y-auto">
            <h2 className="font-semibold text-lg">Nova Automação</h2>
            <input placeholder="Nome" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required className="w-full border rounded-lg px-3 py-2 text-sm" />
            <input placeholder="Descrição" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="w-full border rounded-lg px-3 py-2 text-sm" />
            <div>
              <label className="text-xs text-slate-500">Linguagem</label>
              <select value={form.language} onChange={(e) => setForm({ ...form, language: e.target.value })} className="w-full border rounded-lg px-3 py-2 text-sm">
                <option value="python">Python</option>
                <option value="java">Java (suporte declarado)</option>
                <option value="dotnet">.NET (suporte declarado)</option>
              </select>
            </div>
            {form.language === "python" && (
              <div>
                <label className="text-xs text-slate-500">Código-fonte</label>
                <textarea value={form.source_code} onChange={(e) => setForm({ ...form, source_code: e.target.value })} className="w-full border rounded-lg px-3 py-2 text-sm font-mono text-xs" rows={10} />
              </div>
            )}
            <div className="flex gap-3 justify-end">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-sm border rounded-lg">Cancelar</button>
              <button type="submit" className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg">Criar</button>
            </div>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-3">
          {packages.map((pkg) => (
            <div key={pkg.id} className="bg-white border border-slate-200 rounded-xl p-4">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-semibold text-slate-900">{pkg.name}</h3>
                  {pkg.description && <p className="text-sm text-slate-500">{pkg.description}</p>}
                  <span className={`inline-block mt-1 text-xs px-2 py-0.5 rounded-full font-medium ${pkg.language === "python" ? "bg-blue-100 text-blue-700" : "bg-slate-100 text-slate-600"}`}>
                    {pkg.language.toUpperCase()}
                  </span>
                </div>
                <span className={`text-xs px-2 py-0.5 rounded-full ${pkg.is_active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
                  {pkg.is_active ? "Ativo" : "Inativo"}
                </span>
              </div>
              <div className="flex gap-2">
                <button onClick={() => run(pkg.id)} disabled={running === pkg.id} className="flex items-center gap-1 text-xs bg-green-50 text-green-700 border border-green-200 px-3 py-1.5 rounded hover:bg-green-100 disabled:opacity-40">
                  {running === pkg.id ? <Loader2 size={11} className="animate-spin" /> : <Play size={11} />} Executar
                </button>
                <button onClick={() => securityReview(pkg.id)} disabled={reviewing === pkg.id} className="flex items-center gap-1 text-xs bg-orange-50 text-orange-700 border border-orange-200 px-3 py-1.5 rounded hover:bg-orange-100 disabled:opacity-40">
                  {reviewing === pkg.id ? <Loader2 size={11} className="animate-spin" /> : <Shield size={11} />} Segurança IA
                </button>
              </div>
            </div>
          ))}
          {packages.length === 0 && <div className="text-slate-400 text-center py-12">Nenhuma automação criada.</div>}
        </div>

        <div className="space-y-4">
          {/* Logs */}
          <div className="bg-white border border-slate-200 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-3">
              <Terminal size={16} className="text-slate-500" />
              <h3 className="font-semibold text-sm">Logs de Execução</h3>
            </div>
            <div className="bg-slate-900 rounded-lg p-3 min-h-[150px] font-mono text-xs overflow-y-auto max-h-[200px]">
              {logs.length === 0 ? (
                <p className="text-slate-500">Execute uma automação...</p>
              ) : (
                logs.map((log, i) => (
                  <p key={i} className={log.level === "error" ? "text-red-400" : "text-green-400"}>
                    {`[${log.level.toUpperCase()}] ${log.message}`}
                  </p>
                ))
              )}
            </div>
          </div>

          {/* Security Review */}
          {securityResult && (
            <div className="bg-white border border-slate-200 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <Shield size={16} className="text-orange-500" />
                <h3 className="font-semibold text-sm">Validação de Segurança (IA)</h3>
              </div>
              <div className={`inline-block text-sm font-semibold px-3 py-1 rounded-full mb-3 ${riskColors[securityResult.risk_level]}`}>
                Risco: {securityResult.risk_level.toUpperCase()}
              </div>
              {securityResult.issues.length === 0 ? (
                <p className="text-sm text-green-600 flex items-center gap-1"><Shield size={14} /> Nenhum problema encontrado</p>
              ) : (
                <ul className="space-y-2">
                  {securityResult.issues.map((issue, i) => (
                    <li key={i} className="text-xs text-slate-600 border-l-2 border-orange-400 pl-2">
                      <span className="font-medium">{issue.pattern}</span> — {issue.message}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
