import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Ticket Processor | World-Class SaaS Dashboard",
  description: "Automated customer support ticket analysis with AI - built for non-technical support managers",
  keywords: "AI, ticket processing, support automation, SaaS, analytics",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
