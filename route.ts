import { NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const type = searchParams.get('type')

  if (!type || (type !== 'pre' && type !== 'post')) {
    return NextResponse.json({ error: 'Invalid file type' }, { status: 400 })
  }

  const fileName = type === 'pre' ? 'sample_preCheck.log' : 'sample_postCheck.log'
  const filePath = path.join(process.cwd(), 'public', fileName)

  try {
    const content = fs.readFileSync(filePath, 'utf-8')
    return new NextResponse(content, {
      headers: {
        'Content-Type': 'text/plain',
      },
    })
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to read sample file' },
      { status: 500 }
    )
  }
}
