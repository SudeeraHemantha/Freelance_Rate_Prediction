"use client"

import React from "react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts"

interface RechartsVisualizerProps {
  predictedRate: number
  techStack: string
}

export default function RechartsVisualizer({ predictedRate, techStack }: RechartsVisualizerProps) {
  // Build dynamic chart tiers based on selected technology stack to mimic database distributions
  const getTiers = (tech: string) => {
    switch (tech) {
      case "Rust":
      case "Go":
        return [
          { name: "Low Tier", rate: 55 },
          { name: "Medium Tier", rate: 95 },
          { name: "High Tier", rate: 160 }
        ]
      case "Python":
      case "Kubernetes":
        return [
          { name: "Low Tier", rate: 45 },
          { name: "Medium Tier", rate: 85 },
          { name: "High Tier", rate: 135 }
        ]
      case "React":
      case "Node.js":
        return [
          { name: "Low Tier", rate: 35 },
          { name: "Medium Tier", rate: 70 },
          { name: "High Tier", rate: 110 }
        ]
      default:
        return [
          { name: "Low Tier", rate: 30 },
          { name: "Medium Tier", rate: 60 },
          { name: "High Tier", rate: 90 }
        ]
    }
  }

  const data = getTiers(techStack)

  return (
    <div className="w-full h-80 bg-zinc-950/40 rounded-xl p-6 border border-white/5 flex flex-col justify-between">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h4 className="text-sm font-semibold text-white">Market Rate Distribution ({techStack})</h4>
          <p className="text-xs text-muted-foreground">Typical hourly rate tiers compared to your live prediction.</p>
        </div>
        {predictedRate > 0 && (
          <div className="text-right">
            <span className="text-xs text-muted-foreground font-medium">Your Estimate</span>
            <div className="text-sm font-bold text-blue-400">${predictedRate.toFixed(2)}/hr</div>
          </div>
        )}
      </div>

      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 10, right: 30, left: -25, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
            <XAxis 
              dataKey="name" 
              stroke="#9ca3af" 
              fontSize={11} 
              tickLine={false} 
              axisLine={false} 
            />
            <YAxis 
              stroke="#9ca3af" 
              fontSize={11} 
              tickLine={false} 
              axisLine={false} 
              unit="$" 
            />
            <Tooltip
              contentStyle={{ backgroundColor: "#090d1f", borderColor: "#1f2937", borderRadius: "8px" }}
              labelStyle={{ color: "#fff", fontWeight: "bold" }}
              itemStyle={{ color: "#60a5fa" }}
            />
            <Bar 
              dataKey="rate" 
              fill="#2563eb" 
              radius={[6, 6, 0, 0]} 
              maxBarSize={45} 
            />
            {predictedRate > 0 && (
              <ReferenceLine
                y={predictedRate}
                stroke="#60a5fa"
                strokeDasharray="4 4"
                strokeWidth={2}
                label={{
                  value: `Current prediction: $${predictedRate.toFixed(2)}/hr`,
                  position: "insideBottomRight",
                  fill: "#93c5fd",
                  fontSize: 10,
                  fontWeight: "bold",
                  offset: 8
                }}
              />
            )}
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
