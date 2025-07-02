export interface DiffLine {
  type: "identical" | "added" | "deleted" | "changed" | "empty"
  content: string
  lineNumber: number
}

export interface DiffResult {
  leftContent: DiffLine[]
  rightContent: DiffLine[]
  stats: {
    total: number
    added: number
    deleted: number
    changed: number
  }
}

export function generateDiff(preContent: string, postContent: string): DiffResult {
  console.log('Generating diff...')
  console.log('Pre content length:', preContent.length)
  console.log('Post content length:', postContent.length)

  const preLines = preContent.split("\n")
  const postLines = postContent.split("\n")
  
  console.log('Pre lines:', preLines.length)
  console.log('Post lines:', postLines.length)
  
  const leftContent: DiffLine[] = []
  const rightContent: DiffLine[] = []
  const stats = {
    total: 0,
    added: 0,
    deleted: 0,
    changed: 0
  }

  let i = 0
  let j = 0
  let leftLineNum = 1
  let rightLineNum = 1

  while (i < preLines.length || j < postLines.length) {
    const preLine = preLines[i]
    const postLine = postLines[j]

    if (i >= preLines.length) {
      // Added lines at the end
      rightContent.push({
        type: "added",
        content: postLine,
        lineNumber: rightLineNum++
      })
      leftContent.push({
        type: "empty",
        content: "",
        lineNumber: 0
      })
      stats.added++
      stats.total++
      j++
    } else if (j >= postLines.length) {
      // Deleted lines at the end
      leftContent.push({
        type: "deleted",
        content: preLine,
        lineNumber: leftLineNum++
      })
      rightContent.push({
        type: "empty",
        content: "",
        lineNumber: 0
      })
      stats.deleted++
      stats.total++
      i++
    } else if (preLine === postLine) {
      // Identical lines
      leftContent.push({
        type: "identical",
        content: preLine,
        lineNumber: leftLineNum++
      })
      rightContent.push({
        type: "identical",
        content: postLine,
        lineNumber: rightLineNum++
      })
      i++
      j++
    } else {
      // Lines are different
      const preNext = preLines[i + 1]
      const postNext = postLines[j + 1]

      if (preNext === postLine) {
        // Line was deleted
        leftContent.push({
          type: "deleted",
          content: preLine,
          lineNumber: leftLineNum++
        })
        rightContent.push({
          type: "empty",
          content: "",
          lineNumber: 0
        })
        stats.deleted++
        stats.total++
        i++
      } else if (preLine === postNext) {
        // Line was added
        leftContent.push({
          type: "empty",
          content: "",
          lineNumber: 0
        })
        rightContent.push({
          type: "added",
          content: postLine,
          lineNumber: rightLineNum++
        })
        stats.added++
        stats.total++
        j++
      } else {
        // Line was changed
        leftContent.push({
          type: "changed",
          content: preLine,
          lineNumber: leftLineNum++
        })
        rightContent.push({
          type: "changed",
          content: postLine,
          lineNumber: rightLineNum++
        })
        stats.changed++
        stats.total++
        i++
        j++
      }
    }
  }

  return {
    leftContent,
    rightContent,
    stats
  }
}

export function readFileAsText(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => resolve(e.target?.result as string)
    reader.onerror = (e) => reject(e)
    reader.readAsText(file)
  })
}

export async function compareFiles(preFile: File, postFile: File): Promise<DiffResult> {
  try {
    const [preContent, postContent] = await Promise.all([
      readFileAsText(preFile),
      readFileAsText(postFile)
    ])
    
    return generateDiff(preContent, postContent)
  } catch (error) {
    console.error("Error comparing files:", error)
    throw new Error("Failed to compare files")
  }
}
