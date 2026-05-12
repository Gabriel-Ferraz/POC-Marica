"use client";
import { useState } from "react";
import AppLayout from "@/components/layout/AppLayout";
import { useAuth } from "@/hooks/useAuth";
import api from "@/lib/api";
import { Mic, MicOff, Volume2 } from "lucide-react";

interface Turn { role: "user" | "assistant"; text: string; }

export default function VoiceBotPage() {
  useAuth();
  const [turns, setTurns] = useState<Turn[]>([]);
  const [userText, setUserText] = useState("");
  const [loading, setLoading] = useState(false);

  const simulate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userText.trim()) return;
    setLoading(true);
    setTurns((t) => [...t, { role: "user", text: userText }]);
    try {
      const { data } = await api.post("/api/voice/call/text", { text: userText });
      setTurns((t) => [...t, { role: "assistant", text: data.assistant_text }]);
      setUserText("");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppLayout>
      <h1 className="text-2xl font-bold text-slate-900 mb-2">Chatbot de Voz — Receptivo</h1>
      <p className="text-slate-500 text-sm mb-6">Simule uma chamada receptiva por voz com transcrição e resposta em linguagem natural.</p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white border border-slate-200 rounded-xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
              <Volume2 size={22} className="text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold">Demo de Voz (Modo Texto)</h3>
              <p className="text-xs text-slate-500">Speech-to-text simulado via entrada de texto</p>
            </div>
          </div>

          <div className="bg-slate-50 rounded-lg p-4 min-h-[250px] mb-4 space-y-3 overflow-y-auto">
            {turns.length === 0 && <p className="text-slate-400 text-sm text-center mt-8">A conversa aparecerá aqui...</p>}
            {turns.map((t, i) => (
              <div key={i} className={`flex gap-2 ${t.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`px-3 py-2 rounded-xl text-sm max-w-[80%] ${t.role === "user" ? "bg-blue-600 text-white" : "bg-white border text-slate-800"}`}>
                  {t.role === "assistant" && <p className="text-xs text-slate-400 mb-1 flex items-center gap-1"><Volume2 size={10} /> Assistente</p>}
                  {t.text}
                </div>
              </div>
            ))}
          </div>

          <form onSubmit={simulate} className="flex gap-2">
            <input value={userText} onChange={(e) => setUserText(e.target.value)} placeholder="Digite o que o usuário diria..." className="flex-1 border rounded-lg px-3 py-2 text-sm" />
            <button type="submit" disabled={loading} className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 disabled:opacity-60 flex items-center gap-2">
              <Mic size={14} /> {loading ? "..." : "Enviar"}
            </button>
          </form>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-6">
          <h3 className="font-semibold mb-4">Fluxo Técnico</h3>
          <div className="space-y-3">
            {[
              { step: "1", label: "Entrada de áudio", desc: "Recebe áudio via upload ou stream" },
              { step: "2", label: "Speech-to-Text", desc: "Whisper / gTTS converte fala em texto" },
              { step: "3", label: "NLP Analyze", desc: "Motor NLP extrai intent e entidades" },
              { step: "4", label: "Decisão / Resposta", desc: "Regra de negócio gera resposta textual" },
              { step: "5", label: "Text-to-Speech", desc: "Texto convertido em áudio WAV/MP3" },
              { step: "6", label: "Histórico", desc: "Transcrição salva no banco de dados" },
            ].map((s) => (
              <div key={s.step} className="flex gap-3">
                <div className="w-6 h-6 rounded-full bg-blue-600 text-white text-xs flex items-center justify-center flex-shrink-0">{s.step}</div>
                <div>
                  <p className="text-sm font-medium text-slate-900">{s.label}</p>
                  <p className="text-xs text-slate-500">{s.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
