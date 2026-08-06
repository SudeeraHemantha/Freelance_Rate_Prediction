import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Freelance Rate & Demand Predictor',
  description: 'AI-driven rate estimator and analytics for freelance project payouts.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className="font-sans antialiased bg-background text-foreground bg-grid-pattern min-h-screen">
        {children}
      </body>
    </html>
  )
}
