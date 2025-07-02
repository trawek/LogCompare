"use client"

const modes = {
  single: "single",
  batch: "batch"
} as const;

type Mode = typeof modes[keyof typeof modes];

import { useState, useEffect } from "react"
import type { ComparisonMode } from "@/types/comparison"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { DiffViewer } from "@/components/diff-viewer"
import { StatsDisplay } from "@/components/stats-display"
import { ChartsDisplay } from "@/components/charts-display"
import { BatchComparison } from "@/components/batch-comparison"
import { compareFiles } from "@/lib/diff-utils"
import type { DiffResult } from "@/lib/diff-utils"

export default function Home() {
  const [files, setFiles] = useState<{ pre: File | null; post: File | null }>({
    pre: null,
    post: null,
  })
  const [diffResult, setDiffResult] = useState<DiffResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [mode, setMode] = useState<"single" | "batch">("single")

  useEffect(() => {
    console.log('State updated:', {
      hasPreFile: !!files.pre,
      hasPostFile: !!files.post,
      hasDiffResult: !!diffResult,
      isLoading: loading,
      error
    })
  }, [files, diffResult, loading, error])

  const handleFileChange = (type: "pre" | "post", file: File | null) => {
    console.log(`File change - ${type}:`, file?.name)
    setFiles(prev => ({ ...prev, [type]: file }))
    setDiffResult(null)
    setError(null)
  }

  const loadSampleFiles = async () => {
    setLoading(true)
    setError(null)
    console.log('Loading sample files...')
    
    try {
      const [preResponse, postResponse] = await Promise.all([
        fetch('/api/sample?type=pre'),
        fetch('/api/sample?type=post')
      ])
      
      if (!preResponse.ok || !postResponse.ok) {
        throw new Error('Failed to load sample files')
      }

      const preText = await preResponse.text()
      const postText = await postResponse.text()

      const preFile = new File([preText], 'sample_preCheck.log', { type: 'text/plain' })
      const postFile = new File([postText], 'sample_postCheck.log', { type: 'text/plain' })

      setFiles({ pre: preFile, post: postFile })
      console.log('Sample files loaded successfully')
      const result = await compareFiles(preFile, postFile)
      console.log('Sample files comparison result:', {
        totalChanges: result.stats.total,
        leftContentLines: result.leftContent.length,
        rightContentLines: result.rightContent.length
      })
      setDiffResult(result)
    } catch (err) {
      console.error('Error loading sample files:', err)
      setError(err instanceof Error ? err.message : "Failed to load sample files")
    } finally {
      setLoading(false)
    }
  }

  const handleCompare = async () => {
    if (!files.pre || !files.post) return

    setLoading(true)
    setError(null)
    console.log('Starting comparison...')
    console.log('Pre file:', files.pre.name)
    console.log('Post file:', files.post.name)
    
    try {
      const result = await compareFiles(files.pre, files.post)
      console.log('Comparison result:', {
        totalChanges: result.stats.total,
        leftContentLines: result.leftContent.length,
        rightContentLines: result.rightContent.length
      })
      setDiffResult(result)
    } catch (err) {
      console.error('Comparison error:', err)
      setError(err instanceof Error ? err.message : "Failed to compare files")
    } finally {
      setLoading(false)
    }
  }

  if (mode.n.trawka === "batch") {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8 max-w-6xl">
          <BatchComparison onBack={() => setMode({ kind: "single" })} />
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4 text-gray-900">
            Log Comparison Tool
          </h1>
          <p className="text-lg text-gray-600">
            Compare pre-check and post-check log files with ease
          </p>
          
          <div className="flex justify-center gap-4 mt-6">
            <Button
              onClick={() => setMode({ kind: "single" })}
              className={`px-6 py-3 font-medium transition-colors duration-200 ${
                mode.kind === "single"
                  ? "bg-black hover:bg-gray-900 text-white" 
                  : "border-2 border-black text-black hover:bg-gray-50 bg-white"
              }`}
            >
              Single File Mode
            </Button>
            <Button
              onClick={() => setMode({ kind: "batch" })}
              className={`px-6 py-3 font-medium transition-colors duration-200 ${
                mode.kind === "batch"
                  ? "bg-black hover:bg-gray-900 text-white" 
                  : "border-2 border-black text-black hover:bg-gray-50 bg-white"
              }`}
            >
              Batch Mode (Directory)
            </Button>
          </div>
        </div>

        <Card className="p-8 border-2 border-gray-200 bg-white">
          <div className="grid gap-8">
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Pre-Check Log File
              </label>
              <div className="relative">
                <Input
                  type="file"
                  accept=".log"
                  onChange={(e) => handleFileChange("pre", e.target.files?.[0] || null)}
                  className="w-full file:mr-4 file:py-2 file:px-4 file:border-0 
                           file:text-sm file:bg-black file:text-white
                           hover:file:bg-gray-900 file:cursor-pointer
                           cursor-pointer rounded-lg border-2 border-gray-200
                           focus:outline-none focus:border-gray-400
                           disabled:opacity-50 disabled:cursor-not-allowed"
                  disabled={loading}
                />
              </div>
              {files.pre && (
                <p className="mt-2 text-sm text-gray-600">
                  Selected: {files.pre.name}
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Post-Check Log File
              </label>
              <div className="relative">
                <Input
                  type="file"
                  accept=".log"
                  onChange={(e) => handleFileChange("post", e.target.files?.[0] || null)}
                  className="w-full file:mr-4 file:py-2 file:px-4 file:border-0 
                           file:text-sm file:bg-black file:text-white
                           hover:file:bg-gray-900 file:cursor-pointer
                           cursor-pointer rounded-lg border-2 border-gray-200
                           focus:outline-none focus:border-gray-400
                           disabled:opacity-50 disabled:cursor-not-allowed"
                  disabled={loading}
                />
              </div>
              {files.post && (
                <p className="mt-2 text-sm text-gray-600">
                  Selected: {files.post.name}
                </p>
              )}
            </div>

            <div className="grid gap-4">
              <Button
                onClick={handleCompare}
                disabled={!files.pre || !files.post || loading}
                className="w-full bg-black hover:bg-gray-900 text-white py-6 text-lg font-medium
                         transition-colors duration-200 disabled:bg-gray-300"
              >
                {loading ? "Comparing..." : "Compare Files"}
              </Button>

              <Button
                onClick={loadSampleFiles}
                disabled={loading}
                variant="outline"
                className="w-full border-2 border-black hover:bg-gray-50 text-black py-6 text-lg font-medium
                         transition-colors duration-200 disabled:opacity-50"
              >
                Load Sample Files
              </Button>
            </div>

            {error && (
              <div className="p-4 text-red-700 bg-red-50 rounded-lg border border-red-200">
                {error}
              </div>
            )}
          </div>
        </Card>

        {diffResult && (
          <div className="mt-8 space-y-6">
            <StatsDisplay stats={diffResult.stats} />
            <ChartsDisplay 
              data={[{ 
                stats: diffResult.stats, 
                fileName: files.pre?.name || 'Comparison' 
              }]} 
              title="Visual Analysis"
            />
            <DiffViewer
              leftContent={diffResult.leftContent}
              rightContent={diffResult.rightContent}
              leftTitle={files.pre?.name}
              rightTitle={files.post?.name}
            />
          </div>
        )}

        <div className="mt-8 py-4 text-center text-sm text-gray-500 border-t border-gray-200 bg-white">
          <p>Supports .log files for comparison • Single files and batch directory processing • Visual charts</p>
          <p className="mt-1">Pre/Post Log Comparison Tool v5.3</p>
        </div>
      </div>
    </div>
  )
}
