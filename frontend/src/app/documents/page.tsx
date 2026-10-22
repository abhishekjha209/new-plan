"use client";

import { useEffect, useState, type FormEvent } from "react";
import { authFetch } from "@/lib/auth";

interface Document {
  id: number;
  user_id: number;
  filename: string;
  content: string;
  created_at: string;
}

export default function DocumentsPage() {
  const [docs, setDocs] = useState<Document[]>([]);
  const [filename, setFilename] = useState("");
  const [content, setContent] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const loadDocuments = async () => {
    const res = await authFetch("/documents");
    if (res.ok) {
      setDocs(await res.json());
    }
    setLoading(false);
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const handleUpload = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    const res = await authFetch("/documents", {
      method: "POST",
      body: JSON.stringify({ filename, content }),
    });
    if (!res.ok) {
      setError((await res.json()).detail ?? "Upload failed");
      return;
    }
    setFilename("");
    setContent("");
    loadDocuments();
  };

  return (
    <div className="flex flex-col items-center w-full pt-10">
      <h1 className="text-2xl font-bold w-full max-w-2xl">Documents</h1>

      <div className="w-full max-w-2xl mt-4 flex flex-col gap-2">
        {loading && <p className="text-gray-500">Loading...</p>}
        {!loading && docs.length === 0 && (
          <p className="text-gray-500">
            No documents yet - upload your first one below.
          </p>
        )}
        {docs.map((doc) => (
          <div
            key={doc.id}
            className="border border-gray-200 rounded-lg p-3 flex justify-between items-center"
          >
            <div>
              <p className="font-medium">{doc.filename}</p>
              <p className="text-sm text-gray-500">
                {new Date(doc.created_at).toLocaleString()}
              </p>
            </div>
            <span className="text-sm text-gray-400">#{doc.id}</span>
          </div>
        ))}
      </div>

      <form
        onSubmit={handleUpload}
        className="w-full max-w-2xl mt-6 flex flex-col gap-2"
      >
        <h2 className="font-semibold">Upload a document</h2>
        <input
          type="text"
          placeholder="Filename (e.g. notes.txt)"
          value={filename}
          onChange={(e) => setFilename(e.target.value)}
          required
          className="border border-gray-300 rounded-md p-2"
        />
        <textarea
          placeholder="Paste the document content here..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
          required
          rows={5}
          className="border border-gray-300 rounded-md p-2"
        />
        {error && (
          <p className="text-red-600 text-sm bg-red-50 border border-red-200 rounded-md p-2">
            {error}
          </p>
        )}
        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors"
        >
          Upload
        </button>
      </form>
    </div>
  );
}
