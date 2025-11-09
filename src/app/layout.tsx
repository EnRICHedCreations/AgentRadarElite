import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AgentRadar - Find Frustrated Real Estate Agents",
  description: "Identify motivated listing agents with stale properties",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
