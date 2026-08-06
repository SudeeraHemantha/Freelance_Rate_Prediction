import React, { useState } from "react"
import { clsx } from "clsx"

interface TooltipProps {
  content: string
  children: React.ReactNode
  position?: "top" | "bottom" | "left" | "right"
  className?: string
}

export function Tooltip({ content, children, position = "top", className }: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false)

  const positionClasses = {
    top: "bottom-full mb-2 left-1/2 -translate-x-1/2",
    bottom: "top-full mt-2 left-1/2 -translate-x-1/2",
    left: "right-full mr-2 top-1/2 -translate-y-1/2",
    right: "left-full ml-2 top-1/2 -translate-y-1/2",
  }

  return (
    <div
      className="relative inline-flex items-center"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
      onFocus={() => setIsVisible(true)}
      onBlur={() => setIsVisible(false)}
    >
      {children}
      {isVisible && (
        <div
          role="tooltip"
          className={clsx(
            "absolute z-50 px-2.5 py-1.5 text-xs font-medium text-zinc-100 bg-zinc-900/95 border border-blue-500/30 rounded-lg shadow-xl backdrop-blur-md whitespace-normal max-w-xs transition-all duration-150 animate-in fade-in zoom-in-95 pointer-events-none",
            positionClasses[position],
            className
          )}
        >
          {content}
        </div>
      )}
    </div>
  )
}

export function InfoBadge({ text }: { text: string }) {
  return (
    <Tooltip content={text} position="top">
      <button
        type="button"
        tabIndex={-1}
        className="inline-flex items-center justify-center w-4 h-4 rounded-full bg-zinc-800 border border-white/10 text-[10px] text-zinc-400 hover:text-blue-400 hover:border-blue-500/40 transition-colors ml-1 cursor-help"
        aria-label="Information tip"
      >
        ?
      </button>
    </Tooltip>
  )
}
