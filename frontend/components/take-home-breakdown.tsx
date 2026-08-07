import React from "react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Tooltip, InfoBadge } from "@/components/ui/tooltip"

export interface TakeHomeBreakdownData {
  net_income: number
  tax_buffer: number
  tool_overheads: number
  non_billable_time: number
}

interface TakeHomeBreakdownProps {
  totalPayout: number
  currencySymbol: string
  currencyCode: string
  breakdown?: TakeHomeBreakdownData
}

export function TakeHomeBreakdown({
  totalPayout,
  currencySymbol = "$",
  currencyCode = "USD",
  breakdown,
}: TakeHomeBreakdownProps) {
  if (totalPayout <= 0) return null

  // Fallback calculation if backend breakdown isn't provided directly
  const netIncome = breakdown?.net_income ?? totalPayout * 0.65
  const taxBuffer = breakdown?.tax_buffer ?? totalPayout * 0.20
  const toolOverheads = breakdown?.tool_overheads ?? totalPayout * 0.10
  const nonBillable = breakdown?.non_billable_time ?? totalPayout * 0.05

  const formatCurrency = (val: number) => {
    return `${currencySymbol}${val.toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`
  }

  return (
    <Card className="overflow-hidden border border-white/10 bg-zinc-950/60">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between text-lg font-bold">
          <span className="flex items-center gap-2">
            <span>📊 Take-Home vs. Real Cost Allocation</span>
            <InfoBadge text="Shows real financial distribution of your total payout after accounting for taxes, software overheads, and administrative work." />
          </span>
          <span className="text-xs font-mono px-2.5 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 font-semibold">
            {currencyCode} Metrics
          </span>
        </CardTitle>
        <CardDescription>
          Detailed financial breakdown based on standard freelance cost ratio distributions.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Visual Segmented Progress Bar */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs text-zinc-400 font-medium">
            <span>Financial Distribution Ratio</span>
            <span>Total: {formatCurrency(totalPayout)} {currencyCode}</span>
          </div>

          <div className="h-4 w-full bg-zinc-900 rounded-full overflow-hidden flex p-0.5 border border-white/5 shadow-inner">
            <Tooltip content={`Net Take-Home Salary (65%): ${formatCurrency(netIncome)}`} className="w-[65%]">
              <div className="h-full bg-emerald-500 rounded-l-full hover:brightness-110 transition-all cursor-pointer" />
            </Tooltip>
            <Tooltip content={`Tax & Self-Employment Reserve (20%): ${formatCurrency(taxBuffer)}`} className="w-[20%]">
              <div className="h-full bg-blue-500 hover:brightness-110 transition-all cursor-pointer" />
            </Tooltip>
            <Tooltip content={`Tooling & Hardware Overheads (10%): ${formatCurrency(toolOverheads)}`} className="w-[10%]">
              <div className="h-full bg-amber-500 hover:brightness-110 transition-all cursor-pointer" />
            </Tooltip>
            <Tooltip content={`Non-Billable Time Buffer (5%): ${formatCurrency(nonBillable)}`} className="w-[5%]">
              <div className="h-full bg-purple-500 rounded-r-full hover:brightness-110 transition-all cursor-pointer" />
            </Tooltip>
          </div>
        </div>

        {/* 4-Grid Financial Category Metrics */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {/* Net Income */}
          <div className="p-3.5 rounded-xl bg-emerald-500/5 border border-emerald-500/20 space-y-1">
            <div className="flex items-center justify-between text-[11px] font-semibold text-emerald-400">
              <span>Net Take-Home</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20">65%</span>
            </div>
            <div className="text-lg font-bold text-white tracking-tight">
              {formatCurrency(netIncome)}
            </div>
            <p className="text-[10px] text-zinc-400">Personal net income</p>
          </div>

          {/* Tax Buffer */}
          <div className="p-3.5 rounded-xl bg-blue-500/5 border border-blue-500/20 space-y-1">
            <div className="flex items-center justify-between text-[11px] font-semibold text-blue-400">
              <span>Tax Buffer</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/20">20%</span>
            </div>
            <div className="text-lg font-bold text-white tracking-tight">
              {formatCurrency(taxBuffer)}
            </div>
            <p className="text-[10px] text-zinc-400">Tax & legal reserve</p>
          </div>

          {/* Tool Overheads */}
          <div className="p-3.5 rounded-xl bg-amber-500/5 border border-amber-500/20 space-y-1">
            <div className="flex items-center justify-between text-[11px] font-semibold text-amber-400">
              <span>Tools & SaaS</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20">10%</span>
            </div>
            <div className="text-lg font-bold text-white tracking-tight">
              {formatCurrency(toolOverheads)}
            </div>
            <p className="text-[10px] text-zinc-400">Software & cloud API costs</p>
          </div>

          {/* Non-Billable Time */}
          <div className="p-3.5 rounded-xl bg-purple-500/5 border border-purple-500/20 space-y-1">
            <div className="flex items-center justify-between text-[11px] font-semibold text-purple-400">
              <span>Non-Billable</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-500/20">5%</span>
            </div>
            <div className="text-lg font-bold text-white tracking-tight">
              {formatCurrency(nonBillable)}
            </div>
            <p className="text-[10px] text-zinc-400">Admin & proposal time</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
