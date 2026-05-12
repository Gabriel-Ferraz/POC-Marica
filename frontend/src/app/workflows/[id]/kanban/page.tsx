"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { toast } from "sonner";
import AppLayout from "@/components/layout/AppLayout";
import { useAuth } from "@/hooks/useAuth";
import api from "@/lib/api";
import type { KanbanColumn } from "@/types";
import { Plus, CheckCircle, RotateCcw } from "lucide-react";

export default function KanbanPage() {
  useAuth();
  const { id } = useParams<{ id: string }>();
  const [columns, setColumns] = useState<KanbanColumn[]>([]);
  const [wfName, setWfName] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [selectedProcess, setSelectedProcess] = useState<string | null>(null);
  const [comment, setComment] = useState("");

  const load = async () => {
    const [wf, kb] = await Promise.all([
      api.get(`/api/workflows/${id}`),
      api.get(`/api/workflows/${id}/kanban`),
    ]);
    setWfName(wf.data.name);
    setColumns(kb.data);
  };
  useEffect(() => { if (id) load(); }, [id]);

  const createProcess = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.post("/api/processes", { workflow_id: id, title: newTitle, form_data: {} });
    toast.success("Processo criado");
    setShowCreate(false);
    setNewTitle("");
    load();
  };

  const accept = async (processId: string) => {
    await api.post(`/api/processes/${processId}/accept`, { comment: comment || undefined });
    toast.success("Aceito — avanço automático registrado com hash DLT");
    setSelectedProcess(null);
    setComment("");
    load();
  };

  const returnCard = async (processId: string) => {
    const c = prompt("Motivo da devolução:");
    if (c === null) return;
    await api.post(`/api/processes/${processId}/return`, { comment: c });
    toast.success("Devolvido — hash DLT registrado");
    load();
  };

  return (
    <AppLayout>
      <div className="flex items-center justify-between mb-6">
        <div>
          <p className="text-sm text-slate-500">{wfName}</p>
          <h1 className="text-2xl font-bold text-slate-900">Kanban</h1>
        </div>
        <button onClick={() => setShowCreate(true)} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700">
          <Plus size={16} /> Novo Processo
        </button>
      </div>

      {showCreate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <form onSubmit={createProcess} className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl space-y-4">
            <h2 className="font-semibold text-lg">Novo Processo</h2>
            <input placeholder="Título do processo" value={newTitle} onChange={(e) => setNewTitle(e.target.value)} required className="w-full border rounded-lg px-3 py-2 text-sm" />
            <div className="flex gap-3 justify-end">
              <button type="button" onClick={() => setShowCreate(false)} className="px-4 py-2 text-sm border rounded-lg">Cancelar</button>
              <button type="submit" className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg">Criar</button>
            </div>
          </form>
        </div>
      )}

      <div className="flex gap-4 overflow-x-auto pb-4">
        {columns.map((col) => (
          <div key={col.step.id} className="flex-shrink-0 w-72">
            <div className={`rounded-t-lg px-4 py-3 font-semibold text-sm ${col.step.is_final ? "bg-green-500 text-white" : "bg-slate-700 text-white"}`}>
              {col.step.name}
              <span className="ml-2 bg-white/20 text-white text-xs px-2 py-0.5 rounded-full">{col.processes.length}</span>
            </div>
            <div className="bg-slate-100 rounded-b-lg p-2 min-h-[200px] space-y-2">
              {col.processes.map((proc) => (
                <div key={proc.id} className="bg-white rounded-lg p-3 shadow-sm border border-slate-200">
                  <p className="font-medium text-sm text-slate-900">{proc.title}</p>
                  <p className="text-xs text-slate-400 mt-1">{new Date(proc.created_at).toLocaleDateString("pt-BR")}</p>
                  <div className="flex gap-2 mt-3">
                    <button onClick={() => accept(proc.id)} className="flex items-center gap-1 text-xs bg-green-50 text-green-700 border border-green-200 px-2 py-1 rounded hover:bg-green-100">
                      <CheckCircle size={11} /> Aceitar
                    </button>
                    <button onClick={() => returnCard(proc.id)} className="flex items-center gap-1 text-xs bg-orange-50 text-orange-700 border border-orange-200 px-2 py-1 rounded hover:bg-orange-100">
                      <RotateCcw size={11} /> Devolver
                    </button>
                  </div>
                </div>
              ))}
              {col.processes.length === 0 && (
                <div className="text-center py-8 text-slate-400 text-xs">Vazio</div>
              )}
            </div>
          </div>
        ))}
        {columns.length === 0 && (
          <div className="text-slate-400 py-16 text-center w-full">Nenhuma etapa configurada. Crie etapas primeiro.</div>
        )}
      </div>
    </AppLayout>
  );
}
