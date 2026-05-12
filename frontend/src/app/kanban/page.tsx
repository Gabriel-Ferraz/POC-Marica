"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import AppLayout from "@/components/layout/AppLayout";
import { useAuth } from "@/hooks/useAuth";
import api from "@/lib/api";
import type { Workflow } from "@/types";
import { Kanban } from "lucide-react";

export default function KanbanIndexPage() {
  useAuth();
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  useEffect(() => { api.get("/api/workflows").then((r) => setWorkflows(r.data.filter((w: Workflow) => w.is_active))); }, []);

  return (
    <AppLayout>
      <h1 className="text-2xl font-bold text-slate-900 mb-6">Kanban — Selecionar Fluxo</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {workflows.map((wf) => (
          <Link key={wf.id} href={`/workflows/${wf.id}/kanban`} className="bg-white border border-slate-200 rounded-xl p-5 hover:border-blue-400 hover:shadow-sm transition-all group">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center group-hover:bg-blue-600 transition-colors">
                <Kanban size={18} className="text-blue-600 group-hover:text-white transition-colors" />
              </div>
              <h3 className="font-semibold text-slate-900">{wf.name}</h3>
            </div>
            {wf.description && <p className="text-sm text-slate-500 mt-1">{wf.description}</p>}
            <p className="text-xs text-blue-600 mt-3 group-hover:underline">Abrir Kanban →</p>
          </Link>
        ))}
        {workflows.length === 0 && <div className="text-slate-400 text-center py-16 col-span-3">Nenhum fluxo ativo. Crie um em Fluxos.</div>}
      </div>
    </AppLayout>
  );
}
