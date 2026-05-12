"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { toast } from "sonner";
import AppLayout from "@/components/layout/AppLayout";
import { useAuth } from "@/hooks/useAuth";
import api from "@/lib/api";
import type { WorkflowStep } from "@/types";
import { Plus, Trash2, Clock } from "lucide-react";

export default function StepsPage() {
  useAuth();
  const { id } = useParams<{ id: string }>();
  const [steps, setSteps] = useState<WorkflowStep[]>([]);
  const [wfName, setWfName] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [showSLA, setShowSLA] = useState<string | null>(null);
  const [form, setForm] = useState({ name: "", description: "", order: 0, is_final: false });
  const [slaForm, setSlaForm] = useState({ deadline_hours: 24, warning_hours: 8 });

  const load = async () => {
    const [wf, st] = await Promise.all([
      api.get(`/api/workflows/${id}`),
      api.get(`/api/workflows/${id}/steps`),
    ]);
    setWfName(wf.data.name);
    setSteps(st.data);
  };
  useEffect(() => { if (id) load(); }, [id]);

  const createStep = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.post(`/api/workflows/${id}/steps`, form);
    toast.success("Etapa criada");
    setShowForm(false);
    setForm({ name: "", description: "", order: steps.length, is_final: false });
    load();
  };

  const deleteStep = async (stepId: string) => {
    if (!confirm("Remover etapa?")) return;
    await api.delete(`/api/workflows/${id}/steps/${stepId}`);
    toast.success("Etapa removida");
    load();
  };

  const saveSLA = async (stepId: string) => {
    await api.post(`/api/workflows/${id}/steps/${stepId}/sla`, slaForm);
    toast.success("SLA configurado");
    setShowSLA(null);
  };

  return (
    <AppLayout>
      <div className="flex items-center justify-between mb-6">
        <div>
          <p className="text-sm text-slate-500">Fluxo: {wfName}</p>
          <h1 className="text-2xl font-bold text-slate-900">Etapas</h1>
        </div>
        <button onClick={() => { setForm({ ...form, order: steps.length }); setShowForm(true); }} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700">
          <Plus size={16} /> Nova Etapa
        </button>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <form onSubmit={createStep} className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl space-y-4">
            <h2 className="font-semibold text-lg">Nova Etapa</h2>
            <input placeholder="Nome da etapa" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required className="w-full border rounded-lg px-3 py-2 text-sm" />
            <input placeholder="Descrição" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="w-full border rounded-lg px-3 py-2 text-sm" />
            <div className="flex gap-4">
              <div className="flex-1">
                <label className="text-xs text-slate-500">Ordem</label>
                <input type="number" value={form.order} onChange={(e) => setForm({ ...form, order: +e.target.value })} className="w-full border rounded-lg px-3 py-2 text-sm" />
              </div>
            </div>
            <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={form.is_final} onChange={(e) => setForm({ ...form, is_final: e.target.checked })} /> Etapa final</label>
            <div className="flex gap-3 justify-end">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-sm border rounded-lg">Cancelar</button>
              <button type="submit" className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg">Criar</button>
            </div>
          </form>
        </div>
      )}

      {showSLA && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-sm shadow-xl space-y-4">
            <h2 className="font-semibold text-lg">Configurar SLA</h2>
            <div>
              <label className="text-xs text-slate-500">Prazo (horas)</label>
              <input type="number" value={slaForm.deadline_hours} onChange={(e) => setSlaForm({ ...slaForm, deadline_hours: +e.target.value })} className="w-full border rounded-lg px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="text-xs text-slate-500">Alerta (horas antes)</label>
              <input type="number" value={slaForm.warning_hours} onChange={(e) => setSlaForm({ ...slaForm, warning_hours: +e.target.value })} className="w-full border rounded-lg px-3 py-2 text-sm" />
            </div>
            <div className="flex gap-3 justify-end">
              <button onClick={() => setShowSLA(null)} className="px-4 py-2 text-sm border rounded-lg">Cancelar</button>
              <button onClick={() => saveSLA(showSLA)} className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg">Salvar</button>
            </div>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {steps.map((step, i) => (
          <div key={step.id} className="bg-white border border-slate-200 rounded-xl p-5 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-sm font-bold">{i + 1}</div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold text-slate-900">{step.name}</h3>
                  {step.is_final && <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">Final</span>}
                </div>
                {step.description && <p className="text-sm text-slate-500">{step.description}</p>}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button onClick={() => { setShowSLA(step.id); setSlaForm({ deadline_hours: 24, warning_hours: 8 }); }} className="flex items-center gap-1 text-xs text-slate-600 hover:text-blue-600 border rounded-lg px-3 py-1.5">
                <Clock size={12} /> SLA
              </button>
              <button onClick={() => deleteStep(step.id)} className="text-red-500 hover:text-red-700 p-1.5">
                <Trash2 size={14} />
              </button>
            </div>
          </div>
        ))}
        {steps.length === 0 && (
          <div className="text-center py-16 text-slate-400">Nenhuma etapa criada ainda.</div>
        )}
      </div>
    </AppLayout>
  );
}
