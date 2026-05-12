"use client";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import AppLayout from "@/components/layout/AppLayout";
import { useAuth } from "@/hooks/useAuth";
import api from "@/lib/api";
import type { User } from "@/types";
import { Plus, Trash2 } from "lucide-react";

export default function UsersPage() {
  useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ email: "", full_name: "", password: "", is_superuser: false });

  const load = () => api.get("/api/users").then((r) => setUsers(r.data));
  useEffect(() => { load(); }, []);

  const create = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post("/api/users", form);
      toast.success("Usuário criado");
      setShowForm(false);
      setForm({ email: "", full_name: "", password: "", is_superuser: false });
      load();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Erro ao criar usuário");
    }
  };

  const del = async (id: string) => {
    if (!confirm("Remover usuário?")) return;
    await api.delete(`/api/users/${id}`);
    toast.success("Removido");
    load();
  };

  return (
    <AppLayout>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Usuários</h1>
        <button onClick={() => setShowForm(true)} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 transition-colors">
          <Plus size={16} /> Novo Usuário
        </button>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <form onSubmit={create} className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl space-y-4">
            <h2 className="font-semibold text-lg">Novo Usuário</h2>
            <input placeholder="Nome completo" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} required className="w-full border rounded-lg px-3 py-2 text-sm" />
            <input placeholder="E-mail" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required className="w-full border rounded-lg px-3 py-2 text-sm" />
            <input placeholder="Senha" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required className="w-full border rounded-lg px-3 py-2 text-sm" />
            <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={form.is_superuser} onChange={(e) => setForm({ ...form, is_superuser: e.target.checked })} /> Superusuário</label>
            <div className="flex gap-3 justify-end">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-sm border rounded-lg">Cancelar</button>
              <button type="submit" className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg">Criar</button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="text-left px-6 py-3 font-medium text-slate-600">Nome</th>
              <th className="text-left px-6 py-3 font-medium text-slate-600">E-mail</th>
              <th className="text-left px-6 py-3 font-medium text-slate-600">Perfil</th>
              <th className="text-left px-6 py-3 font-medium text-slate-600">Status</th>
              <th className="px-6 py-3"></th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="border-b border-slate-100 hover:bg-slate-50">
                <td className="px-6 py-3 font-medium">{u.full_name}</td>
                <td className="px-6 py-3 text-slate-600">{u.email}</td>
                <td className="px-6 py-3"><span className={`px-2 py-0.5 rounded-full text-xs font-medium ${u.is_superuser ? "bg-purple-100 text-purple-700" : "bg-slate-100 text-slate-600"}`}>{u.is_superuser ? "Admin" : "Usuário"}</span></td>
                <td className="px-6 py-3"><span className={`px-2 py-0.5 rounded-full text-xs font-medium ${u.is_active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>{u.is_active ? "Ativo" : "Inativo"}</span></td>
                <td className="px-6 py-3 text-right"><button onClick={() => del(u.id)} className="text-red-500 hover:text-red-700"><Trash2 size={14} /></button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AppLayout>
  );
}
