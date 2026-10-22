"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { fetchMe, logout, type Me } from "@/lib/auth";

// Auth-aware navigation item: shows "Login" when logged out, and the user's
// identity + a Logout button when logged in.
// Session restore happens on mount; afterwards, login/logout trigger an
// "auth-changed" event (see lib/auth.ts) because the layout - and this
// component - stays mounted across navigations and never re-mounts.
export default function AuthNav() {
  const router = useRouter();
  const [me, setMe] = useState<Me | null>(null);
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    const check = () => {
      fetchMe().then((user) => {
        setMe(user);
        setChecked(true);
      });
    };
    check();
    window.addEventListener("auth-changed", check);
    return () => window.removeEventListener("auth-changed", check);
  }, []);

  const handleLogout = async () => {
    await logout(); // revokes the refresh token server-side, clears local tokens
    setMe(null);
    router.push("/login");
    router.refresh();
  };

  if (!checked) {
    return <li className="text-gray-400">...</li>;
  }

  if (!me) {
    return (
      <li className="text-gray-600 hover:text-gray-900 cursor-pointer">
        <Link href="/login">Login</Link>
      </li>
    );
  }

  return (
    <li className="flex items-center gap-3">
      <span className="text-gray-600 text-sm">
        {me.name} <span className="text-gray-400">({me.role})</span>
      </span>
      <button
        onClick={handleLogout}
        className="px-3 py-1 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-md transition-colors"
      >
        Logout
      </button>
    </li>
  );
}
