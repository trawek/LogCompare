"use client"

import { useEffect, useRef } from "react"
import { Card } from "@/components/ui/card"

interface DiffLine {
  type: "identical" | "added" | "deleted" | "changed" | "empty"
  content: string
  lineNumber: number
}

interface DiffViewerProps {
  leftContent: DiffLine[]
  rightContent: DiffLine[]
  leftTitle?: string
  rightTitle?: string
}

export function DiffViewer({
  leftContent,
  rightContent,
  leftTitle = "Pre-Check Log",
  rightTitle = "Post-Check Log"
}: DiffViewerProps) {
  console.log('DiffViewer rendering with:', {
    leftContentLength: leftContent.length,
    rightContentLength: rightContent.length,
    leftTitle,
    rightTitle
  })

  const leftRef = useRef<HTMLDivElement>(null)
  const rightRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const leftPanel = leftRef.current
    const rightPanel = rightRef.current

    if (!leftPanel || !rightPanel) return

    let isScrolling = false

    const syncScroll = (source: HTMLDivElement, target: HTMLDivElement) => {
      if (isScrolling) return
      isScrolling = true
      const scrollPercentage = source.scrollTop / (source.scrollHeight - source.clientHeight)
      target.scrollTop = scrollPercentage * (target.scrollHeight - target.clientHeight)
      setTimeout(() => { isScrolling = false }, 10)
    }

    const leftScrollHandler = () => syncScroll(leftPanel, rightPanel)
    const rightScrollHandler = () => syncScroll(rightPanel, leftPanel)

    leftPanel.addEventListener("scroll", leftScrollHandler)
    rightPanel.addEventListener("scroll", rightScrollHandler)

    return () => {
      leftPanel.removeEventListener("scroll", leftScrollHandler)
      rightPanel.removeEventListener("scroll", rightScrollHandler)
    }
  }, [])

  const getLineClass = (type: DiffLine["type"]) => {
    const baseClasses = "min-h-[28px] px-2 py-1 font-mono text-sm whitespace-pre-wrap border-b border-gray-100"
    switch (type) {
      case "added":
        return `${baseClasses} bg-green-50 text-green-800 border-l-4 border-green-500 font-medium`
      case "deleted":
        return `${baseClasses} bg-red-50 text-red-800 border-l-4 border-red-500 font-medium`
      case "changed":
        return `${baseClasses} bg-yellow-50 text-yellow-800 border-l-4 border-yellow-500 font-medium`
      case "empty":
        return `${baseClasses} bg-gray-50 text-gray-400`
      default:
        return `${baseClasses} bg-white text-gray-700`
    }
  }

  return (
    <div className="w-full mt-6">
      <Card className="border-2 border-gray-200 overflow-hidden">
        <div className="flex flex-col md:flex-row h-[80vh] min-h-[400px]">
          {/* Left Panel */}
          <div className="flex-1 flex flex-col border-r border-gray-200 min-w-0 max-w-full">
            <div className="bg-black text-white p-3 text-center font-medium truncate">
              {leftTitle}
            </div>
            <div 
              ref={leftRef}
              className="flex-1 overflow-auto min-w-0 max-w-full"
            >
              {leftContent.map((line, idx) => (
                <div 
                  key={`left-${idx}`}
                  className={getLineClass(line.type)}
                >
                  <div className="flex">
                    <span className="w-12 text-right pr-4 text-gray-500 select-none border-r border-gray-200">
                      {line.lineNumber || ''}
                    </span>
                    <span className="pl-4 flex-1 break-words whitespace-pre-wrap">{line.content}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right Panel */}
          <div className="flex-1 flex flex-col min-w-0 max-w-full">
            <div className="bg-black text-white p-3 text-center font-medium truncate">
              {rightTitle}
            </div>
            <div 
              ref={rightRef}
              className="flex-1 overflow-auto min-w-0 max-w-full"
            >
              {rightContent.map((line, idx) => (
                <div 
                  key={`right-${idx}`}
                  className={getLineClass(line.type)}
                >
                  <div className="flex">
                    <span className="w-12 text-right pr-4 text-gray-500 select-none border-r border-gray-200">
                      {line.lineNumber || ''}
                    </span>
                    <span className="pl-4 flex-1 break-words whitespace-pre-wrap">{line.content}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <div className="flex flex-wrap gap-6 justify-center text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded-sm"></div>
              <span>Added</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-red-500 rounded-sm"></div>
              <span>Deleted</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-yellow-500 rounded-sm"></div>
              <span>Changed</span>
            </div>
          </div>
        </div>
      </Card>
    </div>
  )
}
