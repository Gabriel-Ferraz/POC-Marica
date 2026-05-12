"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard, Users, Building2, Workflow, Kanban,
  Network, FileCode2, Hash, Key, Shield,
  MessageSquare, Mic, Megaphone, ScanText, Zap, LogOut,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/users", label: "Usuários", icon: Users },
  { href: "/departments", label: "Departamentos", icon: Building2 },
  { href: "/workflows", label: "Fluxos", icon: Workflow },
  { href: "/kanban", label: "Kanban", icon: Kanban },
  { href: "/dlt/networks", label: "Redes DLT", icon: Network },
  { href: "/dlt/contracts", label: "Contratos", icon: FileCode2 },
  { href: "/dlt/records", label: "Registros DLT", icon: Hash },
  { href: "/api-keys", label: "API Keys", icon: Key },
  { href: "/endpoint-permissions", label: "Permissões", icon: Shield },
  { href: "/chatbots", label: "Chatbots", icon: MessageSquare },
  { href: "/chat-demo", label: "Demo NLP", icon: MessageSquare },
  { href: "/voice-bot", label: "Voz Receptiva", icon: Mic },
  { href: "/voice-campaigns", label: "Campanhas Voz", icon: Megaphone },
  { href: "/idp", label: "IDP / OCR", icon: ScanText },
  { href: "/automations", label: "Automações", icon: Zap },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { logout } = useAuth();

  return (
    <aside className="fixed inset-y-0 left-0 z-50 w-64 bg-slate-900 text-white flex flex-col">
      <div className="px-6 py-5 border-b border-slate-700">
        <h1 className="text-lg font-bold text-white">POC ICTIM</h1>
        <p className="text-xs text-slate-400 mt-0.5">Pregão 001/2026</p>
      </div>
      <nav className="flex-1 overflow-y-auto py-4">
        {navItems.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex items-center gap-3 px-6 py-2.5 text-sm transition-colors",
              pathname === href || pathname.startsWith(href + "/")
                ? "bg-blue-600 text-white"
                : "text-slate-300 hover:bg-slate-800 hover:text-white"
            )}
          >
            <Icon size={16} />
            {label}
          </Link>
        ))}
      </nav>
      <div className="p-4 border-t border-slate-700">
        <button
          onClick={logout}
          className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors w-full px-2 py-2"
        >
          <LogOut size={16} />
          Sair
        </button>
      </div>
    </aside>
  );
}
