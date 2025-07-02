"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useState } from "react"

interface ChartData {
  stats: {
    total: number
    added: number
    deleted: number
    changed: number
  }
  fileName?: string
}

interface ChartsDisplayProps {
  data: ChartData[]
  title?: string
}

export function ChartsDisplay({ data, title = "Comparison Charts" }: ChartsDisplayProps) {
  const [chartType, setChartType] = useState<"bar" | "pie" | "line">("bar")

  // Calculate totals for all comparisons
  const totals = data.reduce(
    (acc, item) => ({
      total: acc.total + item.stats.total,
      added: acc.added + item.stats.added,
      deleted: acc.deleted + item.stats.deleted,
      changed: acc.changed + item.stats.changed,
    }),
    { total: 0, added: 0, deleted: 0, changed: 0 }
  )

  const BarChart = ({ stats, label }: { stats: any; label: string }) => {
    const maxValue = Math.max(stats.added, stats.deleted, stats.changed, 1)
    
    return (
      <div className="space-y-4">
        <h4 className="font-medium text-center">{label}</h4>
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <span className="w-16 text-sm">Added:</span>
            <div className="flex-1 bg-gray-200 rounded-full h-6 relative">
              <div 
                className="bg-green-500 h-6 rounded-full flex items-center justify-end pr-2"
                style={{ width: `${(stats.added / maxValue) * 100}%` }}
              >
                <span className="text-white text-xs font-medium">{stats.added}</span>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <span className="w-16 text-sm">Deleted:</span>
            <div className="flex-1 bg-gray-200 rounded-full h-6 relative">
              <div 
                className="bg-red-500 h-6 rounded-full flex items-center justify-end pr-2"
                style={{ width: `${(stats.deleted / maxValue) * 100}%` }}
              >
                <span className="text-white text-xs font-medium">{stats.deleted}</span>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <span className="w-16 text-sm">Changed:</span>
            <div className="flex-1 bg-gray-200 rounded-full h-6 relative">
              <div 
                className="bg-yellow-500 h-6 rounded-full flex items-center justify-end pr-2"
                style={{ width: `${(stats.changed / maxValue) * 100}%` }}
              >
                <span className="text-white text-xs font-medium">{stats.changed}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const PieChart = ({ stats, label }: { stats: any; label: string }) => {
    const total = stats.added + stats.deleted + stats.changed
    if (total === 0) return <div className="text-center text-gray-500">No changes to display</div>

    const addedPercent = (stats.added / total) * 100
    const deletedPercent = (stats.deleted / total) * 100
    const changedPercent = (stats.changed / total) * 100

    // Simple CSS-based pie chart
    const pieStyle = {
      background: `conic-gradient(
        #10b981 0deg ${addedPercent * 3.6}deg,
        #ef4444 ${addedPercent * 3.6}deg ${(addedPercent + deletedPercent) * 3.6}deg,
        #f59e0b ${(addedPercent + deletedPercent) * 3.6}deg 360deg
      )`
    }

    return (
      <div className="space-y-4">
        <h4 className="font-medium text-center">{label}</h4>
        <div className="flex flex-col items-center">
          <div 
            className="w-32 h-32 rounded-full border-4 border-white shadow-lg"
            style={pieStyle}
          ></div>
          <div className="mt-4 space-y-2 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded"></div>
              <span>Added: {stats.added} ({addedPercent.toFixed(1)}%)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-red-500 rounded"></div>
              <span>Deleted: {stats.deleted} ({deletedPercent.toFixed(1)}%)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-yellow-500 rounded"></div>
              <span>Changed: {stats.changed} ({changedPercent.toFixed(1)}%)</span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const LineChart = () => {
    if (data.length < 2) return <div className="text-center text-gray-500">Need at least 2 comparisons for trend analysis</div>

    const maxValue = Math.max(...data.map(d => Math.max(d.stats.added, d.stats.deleted, d.stats.changed)), 1)
    const chartHeight = 200
    const chartWidth = 400

    return (
      <div className="space-y-4">
        <h4 className="font-medium text-center">Change Trends</h4>
        <div className="flex justify-center">
          <svg width={chartWidth} height={chartHeight + 40} className="border rounded">
            {/* Grid lines */}
            {[0, 25, 50, 75, 100].map(percent => (
              <line
                key={percent}
                x1="40"
                y1={20 + (chartHeight * percent / 100)}
                x2={chartWidth - 20}
                y2={20 + (chartHeight * percent / 100)}
                stroke="#e5e7eb"
                strokeWidth="1"
              />
            ))}
            
            {/* Y-axis labels */}
            {[0, 25, 50, 75, 100].map(percent => (
              <text
                key={percent}
                x="35"
                y={25 + (chartHeight * (100 - percent) / 100)}
                fontSize="10"
                textAnchor="end"
                fill="#6b7280"
              >
                {Math.round(maxValue * percent / 100)}
              </text>
            ))}

            {/* Lines for each metric */}
            {['added', 'deleted', 'changed'].map((metric, metricIndex) => {
              const color = metric === 'added' ? '#10b981' : metric === 'deleted' ? '#ef4444' : '#f59e0b'
              const points = data.map((d, i) => {
                const x = 40 + (i * (chartWidth - 60) / (data.length - 1))
                const y = 20 + chartHeight - ((d.stats[metric as keyof typeof d.stats] / maxValue) * chartHeight)
                return `${x},${y}`
              }).join(' ')

              return (
                <g key={metric}>
                  <polyline
                    points={points}
                    fill="none"
                    stroke={color}
                    strokeWidth="2"
                  />
                  {data.map((d, i) => {
                    const x = 40 + (i * (chartWidth - 60) / (data.length - 1))
                    const y = 20 + chartHeight - ((d.stats[metric as keyof typeof d.stats] / maxValue) * chartHeight)
                    return (
                      <circle
                        key={i}
                        cx={x}
                        cy={y}
                        r="3"
                        fill={color}
                      />
                    )
                  })}
                </g>
              )
            })}

            {/* X-axis labels */}
            {data.map((d, i) => (
              <text
                key={i}
                x={40 + (i * (chartWidth - 60) / (data.length - 1))}
                y={chartHeight + 35}
                fontSize="10"
                textAnchor="middle"
                fill="#6b7280"
              >
                {d.fileName ? d.fileName.substring(0, 8) + '...' : `File ${i + 1}`}
              </text>
            ))}
          </svg>
        </div>
        
        <div className="flex justify-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded"></div>
            <span>Added</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded"></div>
            <span>Deleted</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-yellow-500 rounded"></div>
            <span>Changed</span>
          </div>
        </div>
      </div>
    )
  }

  return (
    <Card className="p-6 bg-white border-2 border-gray-200">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
          <div className="flex gap-2">
            <Button
              onClick={() => setChartType("bar")}
              variant={chartType === "bar" ? "default" : "outline"}
              size="sm"
              className={chartType === "bar" ? "bg-black text-white" : ""}
            >
              Bar Chart
            </Button>
            <Button
              onClick={() => setChartType("pie")}
              variant={chartType === "pie" ? "default" : "outline"}
              size="sm"
              className={chartType === "pie" ? "bg-black text-white" : ""}
            >
              Pie Chart
            </Button>
            {data.length > 1 && (
              <Button
                onClick={() => setChartType("line")}
                variant={chartType === "line" ? "default" : "outline"}
                size="sm"
                className={chartType === "line" ? "bg-black text-white" : ""}
              >
                Trend Chart
              </Button>
            )}
          </div>
        </div>

        <div className="grid gap-6">
          {chartType === "bar" && (
            <>
              <BarChart stats={totals} label="Overall Summary" />
              {data.length > 1 && (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {data.map((item, index) => (
                    <BarChart
                      key={index}
                      stats={item.stats}
                      label={item.fileName || `Comparison ${index + 1}`}
                    />
                  ))}
                </div>
              )}
            </>
          )}

          {chartType === "pie" && (
            <>
              <PieChart stats={totals} label="Overall Distribution" />
              {data.length > 1 && (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {data.map((item, index) => (
                    <PieChart
                      key={index}
                      stats={item.stats}
                      label={item.fileName || `Comparison ${index + 1}`}
                    />
                  ))}
                </div>
              )}
            </>
          )}

          {chartType === "line" && <LineChart />}
        </div>
      </div>
    </Card>
  )
}
