"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { login, register } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "login") {
        await login(email, password);
      } else {
        await register(name, email, password);
      }
      router.push("/"); // authenticated -> home
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center pt-20 w-full">
      <h1 className="text-3xl font-bold">
        {mode === "login" ? "Login" : "Create account"}
      </h1>

      <div className="mt-4 flex gap-2">
        <button
          onClick={() => setMode("login")}
          className={`px-3 py-1 rounded-md ${mode === "login" ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-700"}`}
        >
          Login
        </button>
        <button
          onClick={() => setMode("register")}
          className={`px-3 py-1 rounded-md ${mode === "register" ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-700"}`}
        >
          Register
        </button>
      </div>

      <form
        onSubmit={handleSubmit}
        className="mt-6 w-full max-w-sm flex flex-col gap-3"
      >
        {mode === "register" && (
          <input
            type="text"
            placeholder="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            className="border border-gray-300 rounded-md p-2"
          />
        )}
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="border border-gray-300 rounded-md p-2"
        />
        <input
          type="password"
          placeholder="Password (min 6 characters)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={6}
          className="border border-gray-300 rounded-md p-2"
        />

        {error && (
          <p className="text-red-600 text-sm bg-red-50 border border-red-200 rounded-md p-2">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={loading}
          className="mt-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-md transition-colors"
        >
          {loading ? "Please wait..." : mode === "login" ? "Login" : "Register"}
        </button>
      </form>
    </div>
  );
}
