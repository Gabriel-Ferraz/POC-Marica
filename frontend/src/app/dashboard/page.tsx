"use client";
import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/AppLayout";
import { useAuth } from "@/hooks/useAuth";
import api from "@/lib/api";
import { Workflow, Database, MessageSquare, Zap } from "lucide-react";

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState({ workflows: 0, processes: 0, chatbots: 0, automations: 0 });

  useEffect(() => {
    Promise.all([
      api.get("/api/workflows").catch(() => ({ data: [] })),
      api.get("/api/chatbots").catch(() => ({ data: [] })),
      api.get("/api/automations").catch(() => ({ data: [] })),
    ]).then(([wf, ch, au]) => {
      setStats({
        workflows: wf.data.length,
        processes: 0,
        chatbots: ch.data.length,
        automations: au.data.length,
      });
    });
  }, []);

  const cards = [
    { label: "Fluxos ativos", value: stats.workflows, icon: Workflow, color: "bg-blue-500" },
    { label: "Redes DLT", value: 1, icon: Database, color: "bg-purple-500" },
    { label: "Chatbots", value: stats.chatbots, icon: MessageSquare, color: "bg-green-500" },
    { label: "Automações", value: stats.automations, icon: Zap, color: "bg-orange-500" },
  ];

  return (
    <AppLayout>
      <div>
        <h1 className="text-2xl font-bold text-slate-900 mb-1">Dashboard</h1>
        <p className="text-slate-500 text-sm mb-8">Bem-vindo, {user?.full_name}</p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
          {cards.map((c) => (
            <div key={c.label} className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex items-center gap-4">
              <div className={`${c.color} rounded-lg p-3 text-white`}>
                <c.icon size={22} />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900">{c.value}</p>
                <p className="text-sm text-slate-500">{c.label}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <h2 className="font-semibold text-slate-800 mb-4">Roteiro de Demonstração</h2>
            <ol className="space-y-2 text-sm text-slate-600 list-decimal list-inside">
              <li>Criar fluxo em <strong>Fluxos → Novo Fluxo</strong></li>
              <li>Adicionar etapas e configurar SLA</li>
              <li>Criar processo no <strong>Kanban</strong></li>
              <li>Aceitar/devolver card e verificar hash DLT</li>
              <li>Configurar rede DLT e contrato inteligente</li>
              <li>Gerar accessKey/secretKey em <strong>API Keys</strong></li>
              <li>Testar chatbot NLP em <strong>Demo NLP</strong></li>
              <li>Fazer upload no <strong>IDP/OCR</strong></li>
              <li>Executar automação Python</li>
            </ol>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <h2 className="font-semibold text-slate-800 mb-4">Status da Plataforma</h2>
            <div className="space-y-3">
              {[
                { label: "Backend FastAPI", status: "online" },
                { label: "PostgreSQL", status: "online" },
                { label: "Redis", status: "online" },
                { label: "Celery Workers", status: "online" },
                { label: "NLP Provider", status: "mock" },
              ].map((s) => (
                <div key={s.label} className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">{s.label}</span>
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${s.status === "online" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}`}>
                    {s.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
