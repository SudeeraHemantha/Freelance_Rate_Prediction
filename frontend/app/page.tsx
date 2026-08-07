"use client"

import React, { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"

// UI Imports
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Tooltip, InfoBadge } from "@/components/ui/tooltip"
import { FeatureGuideModal } from "@/components/feature-guide-modal"
import { TakeHomeBreakdown, TakeHomeBreakdownData } from "@/components/take-home-breakdown"
import RechartsVisualizer from "@/components/recharts-visualizer"

const calculatorSchema = z.object({
  platform: z.string().min(1, "Platform is required"),
  primary_tech: z.string().min(1, "Tech stack is required"),
  project_type: z.string().min(2, "Project type description is required"),
  complexity_level: z.string().min(1, "Complexity is required"),
  estimated_hours: z.number().gt(0, "Estimated hours must be greater than 0"),
  urgency: z.string().min(1, "Urgency level is required"),
  currency: z.string().min(1, "Currency is required"),
  has_auth: z.boolean(),
  has_third_party_apis: z.boolean(),
})

type CalculatorValues = z.infer<typeof calculatorSchema>

export default function PricingCalculatorPage() {
  const [loading, setLoading] = useState(false)
  const [predictedRate, setPredictedRate] = useState<number>(0)
  const [predictedPayout, setPredictedPayout] = useState<number>(0)
  const [currencySymbol, setCurrencySymbol] = useState<string>("$")
  const [currencyCode, setCurrencyCode] = useState<string>("USD")
  const [takeHomeBreakdown, setTakeHomeBreakdown] = useState<TakeHomeBreakdownData | undefined>(undefined)
  const [executionTime, setExecutionTime] = useState<number>(0)
  const [backendError, setBackendError] = useState<string | null>(null)
  
  // Security & Guide Modal state
  const [isGuideOpen, setIsGuideOpen] = useState(false)
  const [tokenStatus, setTokenStatus] = useState<string | null>(null)
  const [apiKey, setApiKey] = useState<string>("freelance_sec_demo_key_2026")

  // React Hook Form binding
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    reset,
    formState: { errors },
  } = useForm<CalculatorValues>({
    resolver: zodResolver(calculatorSchema),
    defaultValues: {
      platform: "Upwork",
      primary_tech: "Python",
      project_type: "Machine Learning Ingestion API",
      complexity_level: "High",
      estimated_hours: 40,
      urgency: "Urgent",
      currency: "USD",
      has_auth: true,
      has_third_party_apis: true,
    },
  })

  // Watch variables
  const watchedTech = watch("primary_tech")
  const watchedAuth = watch("has_auth")
  const watchedThirdParty = watch("has_third_party_apis")
  const watchedCurrency = watch("currency")

  const onSubmit = async (data: CalculatorValues) => {
    setLoading(true)
    setBackendError(null)
    try {
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      }

      if (tokenStatus) {
        headers["Authorization"] = `Bearer ${tokenStatus}`
      } else {
        headers["X-API-Key"] = apiKey
      }

      const response = await fetch("http://localhost:8000/api/v1/predict", {
        method: "POST",
        headers: headers,
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const errJson = await response.json().catch(() => null)
        const msg = errJson?.detail || errJson?.error || `Status ${response.status}`
        throw new Error(msg)
      }

      const resData = await response.json()
      setPredictedRate(parseFloat(resData.predicted_rate))
      setPredictedPayout(parseFloat(resData.predicted_payout))
      setCurrencySymbol(resData.currency_symbol || "$")
      setCurrencyCode(resData.currency || "USD")
      setTakeHomeBreakdown(resData.take_home_breakdown)
      setExecutionTime(resData.execution_time_ms)
    } catch (err: any) {
      console.error("Predict query failed:", err)
      setBackendError(
        err.message || "Could not connect to FastAPI server. Please verify backend is running on port 8000."
      )
    } finally {
      setLoading(false)
    }
  }

  // Handle Token Generation Button
  const handleGenerateToken = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/token", { method: "POST" })
      if (res.ok) {
        const data = await res.json()
        setTokenStatus(data.access_token)
      }
    } catch (e) {
      console.error("Token request failed:", e)
    }
  }

  // Preset Loaders
  const loadPreset = (preset: "python" | "react" | "rust") => {
    if (preset === "python") {
      reset({
        platform: "Upwork",
        primary_tech: "Python",
        project_type: "Build ML Pipeline & FastAPI Endpoint",
        complexity_level: "High",
        estimated_hours: 45,
        urgency: "Urgent",
        currency: watchedCurrency || "USD",
        has_auth: true,
        has_third_party_apis: true,
      })
    } else if (preset === "react") {
      reset({
        platform: "Fiverr",
        primary_tech: "React",
        project_type: "Design Next.js SaaS Analytics Dashboard",
        complexity_level: "Medium",
        estimated_hours: 30,
        urgency: "Medium",
        currency: watchedCurrency || "USD",
        has_auth: true,
        has_third_party_apis: false,
      })
    } else if (preset === "rust") {
      reset({
        platform: "Upwork",
        primary_tech: "Rust",
        project_type: "High-Throughput WebAssembly Engine",
        complexity_level: "High",
        estimated_hours: 60,
        urgency: "High",
        currency: watchedCurrency || "USD",
        has_auth: false,
        has_third_party_apis: true,
      })
    }
  }

  // Handle Clear Results
  const handleClearResults = () => {
    setPredictedRate(0)
    setPredictedPayout(0)
    setTakeHomeBreakdown(undefined)
    setExecutionTime(0)
    setBackendError(null)
  }

  // Handle Export Report
  const handleExportReport = () => {
    const reportData = {
      timestamp: new Date().toISOString(),
      currency: currencyCode,
      currency_symbol: currencySymbol,
      predicted_rate: predictedRate,
      predicted_payout: predictedPayout,
      take_home_breakdown: takeHomeBreakdown,
      execution_latency_ms: executionTime,
      form_parameters: watch(),
    }

    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(reportData, null, 2))
    const downloadAnchor = document.createElement("a")
    downloadAnchor.setAttribute("href", dataStr)
    downloadAnchor.setAttribute("download", `pricing_report_${currencyCode}_${Date.now()}.json`)
    document.body.appendChild(downloadAnchor)
    downloadAnchor.click()
    downloadAnchor.remove()
  }

  // Technology Options
  const techOptions = [
    { label: "Python (ML, Data)", value: "Python" },
    { label: "React (Frontend)", value: "React" },
    { label: "Rust (Systems, Web3)", value: "Rust" },
    { label: "Go (Backend, Microservices)", value: "Go" },
    { label: "Node.js (Backend)", value: "Node.js" },
    { label: "Kubernetes (Cloud Native)", value: "Kubernetes" },
    { label: "Solidity (Blockchain)", value: "Solidity" },
  ]

  // Platform Options
  const platformOptions = [
    { label: "Upwork", value: "Upwork" },
    { label: "Fiverr", value: "Fiverr" },
  ]

  // Complexity Options
  const complexityOptions = [
    { label: "Low Complexity", value: "Low" },
    { label: "Medium Complexity", value: "Medium" },
    { label: "High Complexity", value: "High" },
  ]

  // Urgency Options
  const urgencyOptions = [
    { label: "Low Urgency", value: "Low" },
    { label: "Medium Urgency", value: "Medium" },
    { label: "High Urgency", value: "High" },
    { label: "Urgent/Rush Delivery", value: "Urgent" },
  ]

  // Currency Options
  const currencyOptions = [
    { label: "USD ($)", value: "USD" },
    { label: "EUR (€)", value: "EUR" },
    { label: "GBP (£)", value: "GBP" },
    { label: "LKR (Rs.)", value: "LKR" },
  ]

  return (
    <main className="max-w-6xl mx-auto px-4 py-12">
      {/* Feature Guide Modal */}
      <FeatureGuideModal isOpen={isGuideOpen} onClose={() => setIsGuideOpen(false)} />

      {/* SaaS Branding Header & Action Controls */}
      <header className="mb-10 text-center">
        <div className="flex flex-wrap items-center justify-center gap-3 mb-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
            LightGBM ML Engine v1.0
          </div>

          <Tooltip content="Opens interactive guide explaining every button and action trigger in detail." position="bottom">
            <button
              onClick={() => setIsGuideOpen(true)}
              className="px-3 py-1 rounded-full bg-zinc-900 border border-white/10 hover:border-blue-500/40 text-zinc-300 text-xs font-medium transition-all"
            >
              📖 Feature Guide & How It Works
            </button>
          </Tooltip>

          <Tooltip content="Requests a signed JWT Bearer Token from POST /api/v1/token to authenticate predictions." position="bottom">
            <button
              onClick={handleGenerateToken}
              className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 hover:bg-emerald-500/20 text-emerald-400 text-xs font-medium transition-all"
            >
              {tokenStatus ? "🔒 JWT Auth Active" : "🔑 Generate JWT Security Token"}
            </button>
          </Tooltip>
        </div>

        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-3">
          Freelance <span className="text-gradient">Rate & Demand</span> Predictor
        </h1>
        <p className="text-zinc-400 max-w-xl mx-auto text-sm md:text-base">
          Analyze market rates, calculate payout ranges, and forecast project budgets in real time using automated ML pipelines.
        </p>
      </header>

      {/* Quick Preset Buttons */}
      <div className="mb-8 p-4 rounded-xl bg-zinc-950/60 border border-white/5 flex flex-wrap items-center justify-between gap-4">
        <div className="text-xs font-medium text-zinc-400 flex items-center gap-1">
          <span>Preset Configurations:</span>
          <InfoBadge text="Pre-fills form fields with high-fidelity realistic parameters for instant testing." />
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Tooltip content="Loads Python ML & FastAPI backend project defaults.">
            <Button size="sm" variant="secondary" onClick={() => loadPreset("python")}>
              ⚡ Python ML Preset
            </Button>
          </Tooltip>

          <Tooltip content="Loads Next.js & React SaaS UI project defaults.">
            <Button size="sm" variant="secondary" onClick={() => loadPreset("react")}>
              ⚡ React Dashboard Preset
            </Button>
          </Tooltip>

          <Tooltip content="Loads Rust High-Performance WebAssembly project defaults.">
            <Button size="sm" variant="secondary" onClick={() => loadPreset("rust")}>
              ⚡ Rust Systems Preset
            </Button>
          </Tooltip>
        </div>
      </div>

      {/* Grid Layout splits Form and Analytics Display */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Form Column */}
        <section className="lg:col-span-5">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Pricing Calculator</span>
                <InfoBadge text="Fill in project attributes to run live LightGBM inference." />
              </CardTitle>
              <CardDescription>Input your project parameters to run the predictive rate model.</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
                {/* Platform & Currency Grid */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-zinc-400 uppercase tracking-wider flex items-center">
                      Platform
                      <InfoBadge text="Select target marketplace. Base hourly rates vary by platform distribution." />
                    </label>
                    <Select options={platformOptions} {...register("platform")} />
                    {errors.platform && <p className="text-red-400 text-xs">{errors.platform.message}</p>}
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-zinc-400 uppercase tracking-wider flex items-center">
                      Currency
                      <InfoBadge text="Converts predictions into USD ($), EUR (€), GBP (£), or LKR (Rs.)." />
                    </label>
                    <Select options={currencyOptions} {...register("currency")} />
                  </div>
                </div>

                {/* Tech select */}
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-zinc-400 uppercase tracking-wider flex items-center">
                    Primary Tech Stack
                    <InfoBadge text="Core technology stack heavily dictates market demand and hourly rates." />
                  </label>
                  <Select options={techOptions} {...register("primary_tech")} />
                  {errors.primary_tech && <p className="text-red-400 text-xs">{errors.primary_tech.message}</p>}
                </div>

                {/* Project type text input */}
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-zinc-400 uppercase tracking-wider flex items-center">
                    Project Type Description
                    <InfoBadge text="Specific title or task scope description for the project." />
                  </label>
                  <Input placeholder="e.g. Build API service" {...register("project_type")} />
                  {errors.project_type && <p className="text-red-400 text-xs">{errors.project_type.message}</p>}
                </div>

                {/* Grid for hours & complexity */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-zinc-400 uppercase tracking-wider flex items-center">
                      Estimated Hours
                      <InfoBadge text="Estimated total effort duration required to complete the gig." />
                    </label>
                    <Input type="number" {...register("estimated_hours", { valueAsNumber: true })} />
                    {errors.estimated_hours && <p className="text-red-400 text-xs">{errors.estimated_hours.message}</p>}
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-zinc-400 uppercase tracking-wider flex items-center">
                      Complexity
                      <InfoBadge text="Low (0.85x), Medium (1.0x), High (1.35x) rate multiplier scaling." />
                    </label>
                    <Select options={complexityOptions} {...register("complexity_level")} />
                    {errors.complexity_level && <p className="text-red-400 text-xs">{errors.complexity_level.message}</p>}
                  </div>
                </div>

                {/* Urgency level */}
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-zinc-400 uppercase tracking-wider flex items-center">
                    Urgency Level
                    <InfoBadge text="Rush delivery increases rate payout baseline by up to 25%." />
                  </label>
                  <Select options={urgencyOptions} {...register("urgency")} />
                  {errors.urgency && <p className="text-red-400 text-xs">{errors.urgency.message}</p>}
                </div>

                {/* Switch items */}
                <div className="pt-2 space-y-4 border-t border-white/5">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-xs font-semibold text-white flex items-center">
                        Authentication Flow
                        <InfoBadge text="Adds authentication module complexity ($120 - $200 premium)." />
                      </h4>
                      <p className="text-[11px] text-muted-foreground">Includes login/registration modules.</p>
                    </div>
                    <Switch
                      checked={watchedAuth}
                      onCheckedChange={(checked) => setValue("has_auth", checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-xs font-semibold text-white flex items-center">
                        Third-Party API Integrations
                        <InfoBadge text="Adds external integrations complexity ($100 - $250 premium)." />
                      </h4>
                      <p className="text-[11px] text-muted-foreground">Includes external services integration.</p>
                    </div>
                    <Switch
                      checked={watchedThirdParty}
                      onCheckedChange={(checked) => setValue("has_third_party_apis", checked)}
                    />
                  </div>
                </div>

                {/* Submit button with Tooltip */}
                <Tooltip content="Submits project parameters to POST /api/v1/predict to compute live payout forecasts." className="w-full">
                  <Button type="submit" loading={loading} className="w-full mt-4">
                    🚀 Calculate Payout
                  </Button>
                </Tooltip>
              </form>
            </CardContent>
          </Card>
        </section>

        {/* Display / Results Column */}
        <section className="lg:col-span-7 space-y-8">
          {/* Predicted rate display card */}
          <Card className="overflow-hidden">
            <CardHeader className="pb-4 flex flex-row items-center justify-between">
              <div>
                <CardTitle>Forecast Summary</CardTitle>
                <CardDescription>Live pricing metrics computed using our trained model pipeline.</CardDescription>
              </div>

              {/* Action Buttons for Results */}
              {predictedRate > 0 && (
                <div className="flex items-center gap-2">
                  <Tooltip content="Downloads complete prediction metrics, latency, and form configuration as a JSON file.">
                    <Button size="sm" variant="secondary" onClick={handleExportReport}>
                      📥 Export Report
                    </Button>
                  </Tooltip>

                  <Tooltip content="Clears current prediction calculations and resets baseline overlays.">
                    <Button size="sm" variant="outline" onClick={handleClearResults}>
                      🗑️ Clear
                    </Button>
                  </Tooltip>
                </div>
              )}
            </CardHeader>
            <CardContent>
              {loading ? (
                /* Skeleton Loader */
                <div className="space-y-6 animate-pulse">
                  <div className="h-20 bg-zinc-900/60 rounded-xl" />
                  <div className="grid grid-cols-2 gap-4">
                    <div className="h-16 bg-zinc-900/60 rounded-xl" />
                    <div className="h-16 bg-zinc-900/60 rounded-xl" />
                  </div>
                </div>
              ) : backendError ? (
                /* Service connectivity Error Banner */
                <div className="p-4 rounded-xl border border-red-500/20 bg-red-500/5 text-red-400 text-sm">
                  <h4 className="font-semibold mb-1">Backend Connection Error</h4>
                  <p className="text-xs text-red-400/80">{backendError}</p>
                </div>
              ) : predictedRate > 0 ? (
                /* Active prediction layout */
                <div className="space-y-6">
                  <div className="bg-blue-500/5 border border-blue-500/10 rounded-xl p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                    <div>
                      <span className="text-xs text-muted-foreground uppercase tracking-wider font-semibold">Estimated Payout</span>
                      <div className="text-4xl md:text-5xl font-black text-white mt-1">
                        {currencySymbol}
                        {predictedPayout.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        <span className="text-lg font-normal text-zinc-500 ml-1">{currencyCode}</span>
                      </div>
                    </div>
                    <div className="px-3 py-1.5 rounded-lg bg-zinc-900 text-xs border border-white/5 flex flex-col items-end">
                      <span className="text-muted-foreground">Inference latency</span>
                      <span className="font-mono text-blue-400 font-semibold mt-0.5">{executionTime.toFixed(2)} ms</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 rounded-xl bg-zinc-950/40 border border-white/5">
                      <span className="text-[11px] text-muted-foreground uppercase tracking-wider font-medium">Hourly rate Equivalent</span>
                      <div className="text-2xl font-bold text-white mt-1">{currencySymbol}{predictedRate.toFixed(2)}/hr</div>
                    </div>
                    <div className="p-4 rounded-xl bg-zinc-950/40 border border-white/5">
                      <span className="text-[11px] text-muted-foreground uppercase tracking-wider font-medium">Job Complexity</span>
                      <div className="text-2xl font-bold text-white mt-1">High Tier</div>
                    </div>
                  </div>
                </div>
              ) : (
                /* Waiting State */
                <div className="py-12 text-center border border-dashed border-white/5 rounded-xl">
                  <svg
                    className="mx-auto h-8 w-8 text-zinc-600 mb-3"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="1.5"
                      d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                    />
                  </svg>
                  <p className="text-zinc-500 text-sm">Please set project variables and click "Calculate Payout".</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Take-Home vs. Real Cost Breakdown Component */}
          {predictedRate > 0 && (
            <TakeHomeBreakdown
              totalPayout={predictedPayout}
              currencySymbol={currencySymbol}
              currencyCode={currencyCode}
              breakdown={takeHomeBreakdown}
            />
          )}

          {/* Recharts Analytics display */}
          <RechartsVisualizer predictedRate={predictedRate} techStack={watchedTech} />
        </section>
      </div>
    </main>
  )
}
