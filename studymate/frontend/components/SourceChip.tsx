'use client'

import React from 'react'
import { FileText } from 'lucide-react'
import { CitationResponse } from '@/lib/api'
import { cn } from '@/lib/utils'

interface SourceChipProps {
  citation: CitationResponse
  className?: string
}

export function SourceChip({ citation, className }: SourceChipProps) {
  const formatPageRange = (start: number, end: number) => {
    if (start === end) {
      return `p.${start}`
    }
    return `p.${start}–${end}`
  }

  return (
    <div
      className={cn(
        "inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-800 rounded-md text-xs font-medium",
        className
      )}
      title={`${citation.filename} ${formatPageRange(citation.page_start, citation.page_end)} (Score: ${citation.score.toFixed(3)})`}
    >
      <FileText className="h-3 w-3" />
      <span className="truncate max-w-[120px]">{citation.filename}</span>
      <span className="text-blue-600">
        {formatPageRange(citation.page_start, citation.page_end)}
      </span>
    </div>
  )
}
