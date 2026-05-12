"use client";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import AppLayout from "@/components/layout/AppLayout";
import { useAuth } from "@/hooks/useAuth";
import api from "@/lib/api";
import type { IDPDocument, IDPResult } from "@/types";
import { Upload, FileText, Loader2, CheckCircle } from "lucide-react";

export default function IDPPage() {
  useAuth();
  const [documents, setDocuments] = useState<IDPDocument[]>([]);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState<string | null>(null);
  const [result, setResult] = useState<IDPResult | null>(null);

  const load = () => api.get("/api/idp/documents").then((r) => setDocuments(r.data));
  useEffect(() => { load(); }, []);

  const upload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    const fd = new FormData();
    fd.append("file", file);
    try {
      await api.post("/api/idp/documents", fd, { headers: { "Content-Type": "multipart/form-data" } });
      toast.success("Documento enviado");
      load();
    } catch {
      toast.error("Erro ao enviar documento");
    } finally {
      setUploading(false);
    }
  };

  const process = async (docId: string) => {
    setProcessing(docId);
    setResult(null);
    try {
      await api.post(`/api/idp/documents/${docId}/process`);
      const { data } = await api.get(`/api/idp/documents/${docId}/result`);
      setResult(data);
      toast.success("OCR concluído");
    } catch {
      toast.error("Erro ao processar documento");
    } finally {
      setProcessing(null);
    }
  };

  const exportJson = async (docId: string) => {
    const { data } = await api.get(`/api/idp/documents/${docId}/json`);
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `idp-export-${docId.slice(0, 8)}.json`;
    a.click();
  };

  const confidenceColor = (c: number) => c >= 0.8 ? "text-green-600" : c >= 0.5 ? "text-yellow-600" : "text-red-600";

  return (
    <AppLayout>
      <h1 className="text-2xl font-bold text-slate-900 mb-2">IDP / OCR</h1>
      <p className="text-slate-500 text-sm mb-6">Processamento inteligente de documentos — OCR, classificação automática e exportação JSON.</p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload */}
        <div>
          <label className="block w-full border-2 border-dashed border-slate-300 hover:border-blue-400 rounded-xl p-8 text-center cursor-pointer transition-colors">
            <input type="file" accept=".pdf,.jpg,.jpeg,.png,.bmp,.tiff" onChange={upload} className="hidden" />
            {uploading ? <Loader2 size={32} className="mx-auto text-blue-500 animate-spin mb-2" /> : <Upload size={32} className="mx-auto text-slate-400 mb-2" />}
            <p className="text-sm font-medium text-slate-700">{uploading ? "Enviando..." : "Arraste ou clique para enviar"}</p>
            <p className="text-xs text-slate-400 mt-1">PDF, JPG, PNG, BMP, TIFF</p>
          </label>

          <div className="mt-4 space-y-2">
            {documents.map((doc) => (
              <div key={doc.id} className="bg-white border border-slate-200 rounded-lg p-3 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileText size={16} className="text-slate-400" />
                  <div>
                    <p className="text-sm font-medium text-slate-800">{doc.filename}</p>
                    <p className="text-xs text-slate-400">{doc.mime_type}</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button onClick={() => process(doc.id)} disabled={processing === doc.id} className="text-xs bg-blue-50 text-blue-700 border border-blue-200 px-3 py-1.5 rounded hover:bg-blue-100 disabled:opacity-40 flex items-center gap-1">
                    {processing === doc.id ? <><Loader2 size={11} className="animate-spin" /> Processando</> : "OCR"}
                  </button>
                  <button onClick={() => exportJson(doc.id)} className="text-xs bg-green-50 text-green-700 border border-green-200 px-3 py-1.5 rounded hover:bg-green-100">JSON</button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Result */}
        <div className="bg-white border border-slate-200 rounded-xl p-5">
          <h2 className="font-semibold text-slate-800 mb-4">Resultado do OCR</h2>
          {!result && <p className="text-slate-400 text-sm text-center mt-8">Processe um documento para ver o resultado.</p>}
          {result && (
            <div className="space-y-4 text-sm">
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-slate-50 rounded-lg p-3">
                  <p className="text-xs text-slate-500">Tipo de Documento</p>
                  <p className="font-semibold mt-1">{result.document_type || "—"}</p>
                </div>
                <div className="bg-slate-50 rounded-lg p-3">
                  <p className="text-xs text-slate-500">Confiança</p>
                  <p className={`font-semibold mt-1 ${confidenceColor(result.confidence)}`}>{(result.confidence * 100).toFixed(1)}%</p>
                </div>
                <div className="bg-slate-50 rounded-lg p-3">
                  <p className="text-xs text-slate-500">Manuscrito</p>
                  <p className="font-semibold mt-1">{result.has_handwriting ? "Sim" : "Não"}</p>
                </div>
              </div>

              {result.json_export?.fields && Object.keys(result.json_export.fields as object).length > 0 && (
                <div>
                  <p className="text-xs font-medium text-slate-600 mb-2">Campos Extraídos</p>
                  {Object.entries(result.json_export.fields as Record<string, string>).map(([k, v]) => (
                    <div key={k} className="flex justify-between border-b py-1.5">
                      <span className="text-slate-500">{k}</span>
                      <span className="font-medium">{v}</span>
                    </div>
                  ))}
                </div>
              )}

              {result.raw_text && (
                <div>
                  <p className="text-xs font-medium text-slate-600 mb-2">Texto Bruto (OCR)</p>
                  <pre className="bg-slate-50 border rounded-lg p-3 text-xs text-slate-700 whitespace-pre-wrap max-h-48 overflow-y-auto">{result.raw_text}</pre>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
