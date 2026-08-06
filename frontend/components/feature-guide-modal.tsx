import React from "react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

interface FeatureGuideModalProps {
  isOpen: boolean
  onClose: () => void
}

export function FeatureGuideModal({ isOpen, onClose }: FeatureGuideModalProps) {
  if (!isOpen) return null

  const features = [
    {
      title: "Calculate Payout Button",
      badge: "Primary Trigger",
      color: "bg-blue-500/10 border-blue-500/20 text-blue-400",
      description: "Submits selected gig features (stack, hours, complexity, urgency, auth) to the FastAPI machine learning backend to run inference on the LightGBM Regressor model pipeline."
    },
    {
      title: "Generate Enterprise Security Token",
      badge: "Security",
      color: "bg-emerald-500/10 border-emerald-500/20 text-emerald-400",
      description: "Interacts with POST /api/v1/token to generate a signed JWT Bearer Token. Automatically applies X-API-Key or Authorization headers to verify client permissions."
    },
    {
      title: "Quick Preset Loaders",
      badge: "Presets",
      color: "bg-amber-500/10 border-amber-500/20 text-amber-400",
      description: "Pre-fills form fields with high-fidelity realistic parameters for Python ML, React Frontend, or Systems Engineering gigs for quick model validation."
    },
    {
      title: "Export Forecast Report",
      badge: "Export",
      color: "bg-purple-500/10 border-purple-500/20 text-purple-400",
      description: "Generates and downloads a structured JSON report containing predicted hourly rates, total payout, latency metrics, and feature configurations for client invoicing."
    },
    {
      title: "Clear Forecast Results",
      badge: "Reset",
      color: "bg-zinc-500/10 border-zinc-500/20 text-zinc-400",
      description: "Resets the current pricing calculation display and clears visualizer baseline overlays back to default state."
    },
    {
      title: "Feature Toggles (Auth & Third-Party APIs)",
      badge: "Parameters",
      color: "bg-indigo-500/10 border-indigo-500/20 text-indigo-400",
      description: "Toggles architectural complexity adjustments. Enabling authentication or API integrations adds flat fee premiums ($120 - $200) and increases estimated hours."
    }
  ]

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in">
      <div className="relative w-full max-w-2xl max-h-[85vh] overflow-y-auto bg-zinc-950 border border-white/10 rounded-2xl shadow-2xl p-6">
        <div className="flex items-center justify-between pb-4 border-b border-white/10 mb-6">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <span>Interactive Dashboard Feature Guide</span>
            </h2>
            <p className="text-xs text-zinc-400 mt-1">Detailed guide explaining every button, action trigger, and control in the interface.</p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-zinc-900 border border-white/10 text-zinc-400 hover:text-white transition-colors"
            aria-label="Close modal"
          >
            ✕
          </button>
        </div>

        <div className="space-y-4">
          {features.map((item, idx) => (
            <div key={idx} className="p-4 rounded-xl bg-zinc-900/50 border border-white/5 space-y-1.5">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-white">{item.title}</h3>
                <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${item.color}`}>
                  {item.badge}
                </span>
              </div>
              <p className="text-xs text-zinc-300 leading-relaxed">{item.description}</p>
            </div>
          ))}
        </div>

        <div className="mt-6 pt-4 border-t border-white/10 flex justify-end">
          <Button variant="secondary" onClick={onClose}>
            Close Guide
          </Button>
        </div>
      </div>
    </div>
  )
}
