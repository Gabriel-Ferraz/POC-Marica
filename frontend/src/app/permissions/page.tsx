"use client";
import AppLayout from "@/components/layout/AppLayout";
import { useAuth } from "@/hooks/useAuth";

const modules = [
  { module: "workflows", actions: ["criar", "editar", "excluir", "visualizar"] },
  { module: "processos", actions: ["iniciar", "aceitar", "devolver", "visualizar"] },
  { module: "dlt", actions: ["criar_rede", "criar_contrato", "consultar_registros", "gerar_chaves"] },
  { module: "chatbots", actions: ["criar", "configurar", "conversar"] },
  { module: "idp", actions: ["upload", "processar", "exportar"] },
  { module: "automações", actions: ["criar", "executar", "revisar_segurança"] },
  { module: "usuários", actions: ["criar", "editar", "excluir"] },
];

const roles = ["Administrador", "Gestor", "Operador", "Visualizador"];

export default function PermissionsPage() {
  useAuth();
  return (
    <AppLayout>
      <h1 className="text-2xl font-bold text-slate-900 mb-6">Permissões por Módulo</h1>
      <div className="bg-white rounded-xl border border-slate-200 overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-slate-600">Módulo / Ação</th>
              {roles.map((r) => <th key={r} className="text-center px-4 py-3 font-medium text-slate-600">{r}</th>)}
            </tr>
          </thead>
          <tbody>
            {modules.map((mod) =>
              mod.actions.map((action, i) => (
                <tr key={`${mod.module}-${action}`} className={`border-b hover:bg-slate-50 ${i === 0 ? "border-t-2 border-slate-300" : ""}`}>
                  <td className="px-4 py-2.5">
                    {i === 0 && <span className="text-xs font-semibold text-slate-500 uppercase">{mod.module}</span>}
                    <p className="text-slate-700">{action}</p>
                  </td>
                  <td className="px-4 py-2.5 text-center text-green-500">✓</td>
                  <td className="px-4 py-2.5 text-center text-green-500">{["criar", "editar", "excluir", "usuários"].includes(action) ? "—" : "✓"}</td>
                  <td className="px-4 py-2.5 text-center text-green-500">{action === "visualizar" || action === "consultar_registros" ? "✓" : "—"}</td>
                  <td className="px-4 py-2.5 text-center text-green-500">{action === "visualizar" || action === "consultar_registros" ? "✓" : "—"}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </AppLayout>
  );
}
