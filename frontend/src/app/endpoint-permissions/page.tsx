"use client";
import AppLayout from "@/components/layout/AppLayout";
import { useAuth } from "@/hooks/useAuth";
import { Shield, Key, Lock } from "lucide-react";

const endpoints = [
  { method: "GET", path: "/api/dlt/records", auth: "JWT + API Key", desc: "Consultar registros DLT" },
  { method: "POST", path: "/api/dlt/records", auth: "API Key", desc: "Gravar registro DLT" },
  { method: "GET", path: "/api/dlt/records/{hash}", auth: "JWT + API Key", desc: "Buscar por hash" },
  { method: "POST", path: "/api/processes/{id}/accept", auth: "JWT", desc: "Aceitar processo" },
  { method: "POST", path: "/api/processes/{id}/return", auth: "JWT", desc: "Devolver processo" },
  { method: "POST", path: "/api/nlp/analyze", auth: "JWT", desc: "Analisar texto com NLP" },
  { method: "POST", path: "/api/idp/documents/{id}/process", auth: "JWT", desc: "Processar OCR" },
  { method: "POST", path: "/api/automations/{id}/run", auth: "JWT", desc: "Executar automação" },
];

const methodColors: Record<string, string> = {
  GET: "bg-green-100 text-green-700",
  POST: "bg-blue-100 text-blue-700",
  PUT: "bg-yellow-100 text-yellow-700",
  DELETE: "bg-red-100 text-red-700",
};

export default function EndpointPermissionsPage() {
  useAuth();
  return (
    <AppLayout>
      <h1 className="text-2xl font-bold text-slate-900 mb-2">Permissões de Endpoints</h1>
      <p className="text-slate-500 text-sm mb-6">Controle de acesso por rota — autenticação JWT e API Keys (accessKey/secretKey).</p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {[
          { icon: Key, label: "JWT Bearer", desc: "Token para usuários autenticados via login", color: "bg-blue-100 text-blue-600" },
          { icon: Lock, label: "API Key", desc: "accessKey + secretKey nos headers X-Access-Key e X-Secret-Key", color: "bg-purple-100 text-purple-600" },
          { icon: Shield, label: "Dupla Auth", desc: "Endpoints críticos exigem JWT e API Key simultaneamente", color: "bg-orange-100 text-orange-600" },
        ].map((c) => (
          <div key={c.label} className="bg-white border border-slate-200 rounded-xl p-4 flex gap-3">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${c.color}`}><c.icon size={18} /></div>
            <div><p className="font-semibold text-sm">{c.label}</p><p className="text-xs text-slate-500 mt-0.5">{c.desc}</p></div>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <div className="px-6 py-3 bg-slate-50 border-b">
          <h2 className="font-semibold text-slate-800 text-sm">Endpoints Protegidos</h2>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-slate-50">
              <th className="text-left px-4 py-3 font-medium text-slate-600">Método</th>
              <th className="text-left px-4 py-3 font-medium text-slate-600">Rota</th>
              <th className="text-left px-4 py-3 font-medium text-slate-600">Autenticação</th>
              <th className="text-left px-4 py-3 font-medium text-slate-600">Descrição</th>
            </tr>
          </thead>
          <tbody>
            {endpoints.map((ep, i) => (
              <tr key={i} className="border-b hover:bg-slate-50">
                <td className="px-4 py-3"><span className={`text-xs font-semibold px-2 py-0.5 rounded ${methodColors[ep.method]}`}>{ep.method}</span></td>
                <td className="px-4 py-3 font-mono text-xs text-slate-700">{ep.path}</td>
                <td className="px-4 py-3"><span className="text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded-full">{ep.auth}</span></td>
                <td className="px-4 py-3 text-slate-600">{ep.desc}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-6 bg-slate-900 text-white rounded-xl p-5">
        <h3 className="font-semibold mb-3 text-sm">Exemplo de chamada autenticada com API Keys</h3>
        <pre className="text-xs text-green-400 overflow-x-auto">{`curl -X GET https://api.poc-ictim.local/api/dlt/records \\
  -H "X-Access-Key: ak_your_access_key_here" \\
  -H "X-Secret-Key: sk_your_secret_key_here" \\
  -H "Authorization: Bearer your_jwt_token"`}</pre>
      </div>
    </AppLayout>
  );
}
