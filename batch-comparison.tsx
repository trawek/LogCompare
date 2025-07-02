"use client"

import { useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { DiffViewer } from "./diff-viewer"
import { ChartsDisplay } from "./charts-display"
import { compareFiles } from "@/lib/diff-utils"
import type { DiffResult } from "@/lib/diff-utils"

interface FileComparison {
  id: string
  preFile: File
  postFile: File
  result?: DiffResult
  status: "pending" | "processing" | "completed" | "error"
  error?: string
}

interface BatchComparisonProps {
  onBack: () => void
}

export function BatchComparison({ onBack }: BatchComparisonProps) {
  const [comparisons, setComparisons] = useState<FileComparison[]>([])
  const [processing, setProcessing] = useState(false)
  const [selectedComparison, setSelectedComparison] = useState<string | null>(null)

  const handleDirectoryUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || [])
    const logFiles = files.filter(file => file.name.endsWith('.log'))
    
    // Group files by IP address pattern
    const fileGroups: { [key: string]: { pre?: File; post?: File } } = {}
    
    logFiles.forEach(file => {
      const match = file.name.match(/(\d+\.\d+\.\d+\.\d+)_(preCheck|postCheck)\.log/)
      if (match) {
        const [, ip, type] = match
        if (!fileGroups[ip]) fileGroups[ip] = {}
        if (type === 'preCheck') {
          fileGroups[ip].pre = file
        } else if (type === 'postCheck') {
          fileGroups[ip].post = file
        }
      }
    })

    // Create comparison pairs
    const newComparisons: FileComparison[] = []
    Object.entries(fileGroups).forEach(([ip, files]) => {
      if (files.pre && files.post) {
        newComparisons.push({
          id: ip,
          preFile: files.pre,
          postFile: files.post,
          status: "pending"
        })
      }
    })

    setComparisons(newComparisons)
  }

  const processAllComparisons = async () => {
    setProcessing(true)
    
    for (let i = 0; i < comparisons.length; i++) {
      const comparison = comparisons[i]
      
      setComparisons(prev => prev.map(c => 
        c.id === comparison.id ? { ...c, status: "processing" } : c
      ))

      try {
        const result = await compareFiles(comparison.preFile, comparison.postFile)
        setComparisons(prev => prev.map(c => 
          c.id === comparison.id ? { ...c, result, status: "completed" } : c
        ))
      } catch (error) {
        setComparisons(prev => prev.map(c => 
          c.id === comparison.id ? { 
            ...c, 
            status: "error", 
            error: error instanceof Error ? error.message : "Unknown error"
          } : c
        ))
      }
    }
    
    setProcessing(false)
  }

  const completedCount = comparisons.filter(c => c.status === "completed").length
  const progressPercentage = comparisons.length > 0 ? (completedCount / comparisons.length) * 100 : 0

  if (selectedComparison) {
    const comparison = comparisons.find(c => c.id === selectedComparison)
    if (comparison?.result) {
      return (
        <div className="space-y-6">
          <div className="flex items-center gap-4">
            <Button 
              onClick={() => setSelectedComparison(null)}
              variant="outline"
            >
              ← Back to Summary
            </Button>
            <h2 className="text-xl font-semibold">Host: {comparison.id}</h2>
          </div>
          
          <DiffViewer
            leftContent={comparison.result.leftContent}
            rightContent={comparison.result.rightContent}
            leftTitle={comparison.preFile.name}
            rightTitle={comparison.postFile.name}
          />
        </div>
      )
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button onClick={onBack} variant="outline">
          ← Back to Single File Mode
        </Button>
        <h2 className="text-xl font-semibold">Batch Log Comparison</h2>
      </div>

      <Card className="p-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              Select Directory with Log Files
            </label>
            <input
              type="file"
              {...({ webkitdirectory: "" } as any)}
              multiple
              onChange={handleDirectoryUpload}
              className="w-full p-3 border-2 border-gray-200 rounded-lg"
              disabled={processing}
            />
            <p className="mt-2 text-sm text-gray-600">
              Select a directory containing *_preCheck.log and *_postCheck.log files
            </p>
          </div>

          {comparisons.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <span className="text-sm font-medium">
                  Found {comparisons.length} file pairs
                </span>
                <Button
                  onClick={processAllComparisons}
                  disabled={processing}
                  className="bg-black hover:bg-gray-900 text-white"
                >
                  {processing ? "Processing..." : "Compare All Files"}
                </Button>
              </div>

              {processing && (
                <div className="space-y-2">
                  <Progress value={progressPercentage} className="w-full" />
                  <p className="text-sm text-gray-600">
                    Processing {completedCount} of {comparisons.length} comparisons
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </Card>

      {comparisons.length > 0 && completedCount > 0 && (
        <ChartsDisplay 
          data={comparisons
            .filter(c => c.result)
            .map(c => ({ 
              stats: c.result!.stats, 
              fileName: c.id 
            }))} 
          title="Batch Comparison Charts"
        />
      )}

      {comparisons.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Comparison Results</h3>
          <div className="space-y-2">
            {comparisons.map((comparison) => (
              <div
                key={comparison.id}
                className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
              >
                <div className="flex items-center gap-4">
                  <span className="font-medium">{comparison.id}</span>
                  <span className={`px-2 py-1 rounded text-xs ${
                    comparison.status === "completed" ? "bg-green-100 text-green-800" :
                    comparison.status === "processing" ? "bg-blue-100 text-blue-800" :
                    comparison.status === "error" ? "bg-red-100 text-red-800" :
                    "bg-gray-100 text-gray-800"
                  }`}>
                    {comparison.status}
                  </span>
                  {comparison.result && (
                    <span className="text-sm text-gray-600">
                      {comparison.result.stats.total} changes
                    </span>
                  )}
                </div>
                
                {comparison.status === "completed" && comparison.result && (
                  <Button
                    onClick={() => setSelectedComparison(comparison.id)}
                    variant="outline"
                    size="sm"
                  >
                    View Details
                  </Button>
                )}
                
                {comparison.status === "error" && (
                  <span className="text-sm text-red-600">{comparison.error}</span>
                )}
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}
