"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import type { User } from "@/types";

export function useAuth() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem("user");
    if (!stored) {
      router.replace("/login");
      return;
    }
    setUser(JSON.parse(stored));
  }, [router]);

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    router.replace("/login");
  };

  return { user, logout };
}
