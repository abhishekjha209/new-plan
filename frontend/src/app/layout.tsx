import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Link from "next/link";
import AuthNav from "@/components/AuthNav";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI Knowledge Platform",
  description: "Chat with your documents",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <nav className="bg-white p-4 shadow-md flex justify-center w-full">
        <ul className="flex items-center justify-between gap-4">
          <li className="text-gray-600 hover:text-gray-900 cursor-pointer">
            <Link href="/">Home</Link>
          </li>
          <li className="text-gray-600 hover:text-gray-900 cursor-pointer">
            <Link href="/chat">Chat</Link>
          </li>
          <li className="text-gray-600 hover:text-gray-900 cursor-pointer">
            <Link href="/documents">Documents</Link>
          </li>
          <AuthNav />
        </ul>
      </nav>
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
