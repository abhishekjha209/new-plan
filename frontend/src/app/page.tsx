"use client";

import { useState } from "react";

export default function Home() {
  const [status, setStatus] = useState<string>("");

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
