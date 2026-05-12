"use client";
import { useEffect, useRef, useState } from "react";
import AppLayout from "@/components/layout/AppLayout";
import { useAuth } from "@/hooks/useAuth";
import api from "@/lib/api";
import type { Chatbot } from "@/types";
import { Send, Bot, User } from "lucide-react";

interface Message { role: "user" | "assistant"; content: string; nlp?: Record<string, unknown>; }

export default function ChatDemoPage() {
  useAuth();
  const [chatbots, setChatbots] = useState<Chatbot[]>([]);
  const [selectedBot, setSelectedBot] = useState("");
  const [sessionId] = useState(() => crypto.randomUUID());
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api.get("/api/chatbots").then((r) => {
      setChatbots(r.data);
      if (r.data[0]) setSelectedBot(r.data[0].id);
    });
  }, []);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const send = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !selectedBot) return;
    const userMsg = input.trim();
    setInput("");
    setMessages((m) => [...m, { role: "user", content: userMsg }]);
    setLoading(true);
    try {
      const { data } = await api.post(`/api/chatbots/${selectedBot}/message`, { content: userMsg, session_id: sessionId });
      setMessages((m) => [...m, { role: "assistant", content: data.content, nlp: data.nlp_result }]);
    } catch {
      setMessages((m) => [...m, { role: "assistant", content: "Erro ao processar. Tente novamente." }]);
    } finally {
      setLoading(false);
    }
  };

  const [nlpText, setNlpText] = useState("");
  const [nlpResult, setNlpResult] = useState<Record<string, unknown> | null>(null);

  const analyzeNLP = async () => {
    if (!nlpText) return;
    const { data } = await api.post("/api/nlp/analyze", { text: nlpText });
    setNlpResult(data);
  };

  return (
    <AppLayout>
      <h1 className="text-2xl font-bold text-slate-900 mb-6">Demo NLP & Chatbot</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chat */}
        <div className="bg-white border border-slate-200 rounded-xl flex flex-col h-[600px]">
          <div className="px-4 py-3 border-b flex items-center gap-3">
            <Bot size={18} className="text-blue-600" />
            <select value={selectedBot} onChange={(e) => setSelectedBot(e.target.value)} className="text-sm border rounded px-2 py-1 flex-1">
              {chatbots.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
            </select>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.length === 0 && (
              <div className="text-center text-slate-400 text-sm mt-8">
                <Bot size={32} className="mx-auto mb-2 text-slate-300" />
                Inicie uma conversa...
              </div>
            )}
            {messages.map((msg, i) => (
              <div key={i} className={`flex gap-2 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                {msg.role === "assistant" && <div className="w-7 h-7 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0"><Bot size={14} className="text-blue-600" /></div>}
                <div className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm ${msg.role === "user" ? "bg-blue-600 text-white rounded-br-sm" : "bg-slate-100 text-slate-900 rounded-bl-sm"}`}>
                  {msg.content}
                  {msg.nlp && msg.role === "assistant" && (
                    <div className="mt-2 pt-2 border-t border-slate-200 text-xs text-slate-500 space-y-0.5">
                      <div>Intenção: <span className="font-medium text-slate-700">{String(msg.nlp.intent)}</span></div>
                      <div>Confiança: <span className="font-medium text-slate-700">{(Number(msg.nlp.confidence) * 100).toFixed(0)}%</span></div>
                    </div>
                  )}
                </div>
                {msg.role === "user" && <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0"><User size={14} className="text-white" /></div>}
              </div>
            ))}
            {loading && (
              <div className="flex gap-2 justify-start">
                <div className="w-7 h-7 rounded-full bg-blue-100 flex items-center justify-center"><Bot size={14} className="text-blue-600" /></div>
                <div className="bg-slate-100 rounded-2xl px-4 py-2.5 text-sm text-slate-400">Digitando...</div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          <form onSubmit={send} className="p-3 border-t flex gap-2">
            <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Digite sua mensagem..." className="flex-1 border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            <button type="submit" disabled={loading} className="bg-blue-600 text-white rounded-lg px-4 py-2 hover:bg-blue-700 disabled:opacity-60"><Send size={16} /></button>
          </form>
        </div>

        {/* NLP Playground */}
        <div className="bg-white border border-slate-200 rounded-xl p-5">
          <h2 className="font-semibold text-slate-800 mb-4">NLP Playground</h2>
          <p className="text-sm text-slate-500 mb-4">Analise texto diretamente via motor NLP sem conversa.</p>
          <textarea value={nlpText} onChange={(e) => setNlpText(e.target.value)} placeholder="Digite um texto para analisar..." className="w-full border rounded-lg px-3 py-2 text-sm" rows={5} />
          <button onClick={analyzeNLP} disabled={!nlpText} className="mt-3 w-full bg-purple-600 text-white py-2 rounded-lg text-sm hover:bg-purple-700 disabled:opacity-40">Analisar com NLP</button>

          {nlpResult && (
            <div className="mt-4 bg-slate-50 border rounded-lg p-4 text-sm space-y-2">
              <div className="flex justify-between"><span className="text-slate-500">Intenção:</span><span className="font-semibold">{String(nlpResult.intent)}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Confiança:</span><span className="font-semibold">{(Number(nlpResult.confidence) * 100).toFixed(1)}%</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Sentimento:</span><span className="font-semibold">{String(nlpResult.sentiment)}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Ação sugerida:</span><span className="font-semibold">{String(nlpResult.suggested_action || "—")}</span></div>
              <div>
                <span className="text-slate-500">Entidades:</span>
                <pre className="mt-1 text-xs bg-white border rounded p-2 overflow-x-auto">{JSON.stringify(nlpResult.entities, null, 2)}</pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
