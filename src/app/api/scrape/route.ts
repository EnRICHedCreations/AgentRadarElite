import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

export const maxDuration = 60; // Set timeout to 60 seconds

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Call the Python script
    const pythonScript = path.join(process.cwd(), 'api', 'scrape.py');

    return new Promise((resolve) => {
      const python = spawn('python3', [pythonScript]);

      let output = '';
      let errorOutput = '';

      // Send the request body to Python script via stdin
      python.stdin.write(JSON.stringify(body));
      python.stdin.end();

      python.stdout.on('data', (data) => {
        output += data.toString();
      });

      python.stderr.on('data', (data) => {
        errorOutput += data.toString();
        console.error('[Python Error]', data.toString());
      });

      python.on('close', (code) => {
        if (code !== 0) {
          console.error('[Python Script Failed]', errorOutput);
          resolve(NextResponse.json(
            { success: false, error: errorOutput || 'Python script failed' },
            { status: 500 }
          ));
          return;
        }

        try {
          const result = JSON.parse(output);
          resolve(NextResponse.json(result));
        } catch (parseError) {
          console.error('[JSON Parse Error]', parseError);
          resolve(NextResponse.json(
            { success: false, error: 'Failed to parse Python output', output },
            { status: 500 }
          ));
        }
      });
    });
  } catch (error) {
    console.error('[API Error]', error);
    return NextResponse.json(
      { success: false, error: String(error) },
      { status: 500 }
    );
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}
