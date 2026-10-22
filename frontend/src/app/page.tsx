"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { fetchMe, logout, type Me } from "@/lib/auth";

export default function Home() {
  const router = useRouter();
  const [status, setStatus] = useState<string>("");
  const [me, setMe] = useState<Me | null>(null);
  const [checked, setChecked] = useState(false);

  // Session check on load: fetchMe transparently refreshes an expired access
  // token via authFetch, so this is also the session-restore path.
  useEffect(() => {
    fetchMe().then((user) => {
      setMe(user);
      setChecked(true);
    });
  }, []);

  const handleLogout = async () => {
    await logout(); // revokes the refresh token server-side, clears local tokens
    setMe(null);
    router.push("/login");
    router.refresh();
  };

  const checkHealth = async () => {
    try {
      // Read the API URL from environment variables, fallback to local docker container
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

      // Hit the FastAPI backend (either local or live cloud)
      const res = await fetch(`${apiBaseUrl}/health`);
      const data = await res.json();
      setStatus(data.message);
    } catch (err) {
      setStatus("Error connecting to backend: Is the server running?");
    }
  };

  return (
    <div className="flex flex-col items-center justify-start pt-20 w-full">
      <h1 className="text-4xl font-bold">AI Knowledge Platform</h1>

      {checked && (
        <div
          className={`mt-8 p-4 border rounded-md w-full max-w-md ${
            me
              ? "border-green-200 bg-green-50"
              : "border-gray-200 bg-gray-50"
          }`}
        >
          {me ? (
            <div className="text-left">
              <p className="text-green-800 font-medium">
                ✓ Logged in as {me.name}
              </p>
              <p className="text-sm text-gray-600 mt-1">
                {me.email} · role: <span className="font-medium">{me.role}</span>
              </p>
              <div className="mt-3 flex gap-4 text-sm items-center">
                <Link href="/documents" className="text-blue-600 hover:underline">
                  Your documents →
                </Link>
                <Link href="/chat" className="text-blue-600 hover:underline">
                  Chat →
                </Link>
                <button
                  onClick={handleLogout}
                  className="ml-auto px-3 py-1 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-md transition-colors"
                >
                  Logout
                </button>
              </div>
            </div>
          ) : (
            <p className="text-gray-600">
              Not logged in.{" "}
              <Link href="/login" className="text-blue-600 hover:underline">
                Login or register →
              </Link>
            </p>
          )}
        </div>
      )}

      <button
        onClick={checkHealth}
        className="mt-8 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors"
      >
        Test Backend Connection
      </button>

      {status && (
        <div className="mt-4 p-4 border border-gray-200 rounded-md bg-gray-50">
          <p className="text-lg text-gray-800">{status}</p>
        </div>
      )}
    </div>
  );
}
