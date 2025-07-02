"use client"

import { Card } from "@/components/ui/card"

interface StatsDisplayProps {
  stats: {
    total: number
    added: number
    deleted: number
    changed: number
  }
}

export function StatsDisplay({ stats }: StatsDisplayProps) {
  console.log('StatsDisplay rendering with stats:', stats)
  
  return (
    <Card className="p-6 bg-white mb-6 border-2 border-gray-200">
      <h2 className="text-xl font-semibold mb-4 text-gray-900">Comparison Statistics</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-lg bg-gray-50 border-2 border-gray-200">
          <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
          <div className="text-sm text-gray-600">Total Changes</div>
        </div>
        <div className="p-4 rounded-lg bg-green-50 border-2 border-green-200">
          <div className="text-2xl font-bold text-green-700">{stats.added}</div>
          <div className="text-sm text-green-600">Added Lines</div>
        </div>
        <div className="p-4 rounded-lg bg-red-50 border-2 border-red-200">
          <div className="text-2xl font-bold text-red-700">{stats.deleted}</div>
          <div className="text-sm text-red-600">Deleted Lines</div>
        </div>
        <div className="p-4 rounded-lg bg-yellow-50 border-2 border-yellow-200">
          <div className="text-2xl font-bold text-yellow-700">{stats.changed}</div>
          <div className="text-sm text-yellow-600">Changed Lines</div>
        </div>
      </div>
    </Card>
  )
}
