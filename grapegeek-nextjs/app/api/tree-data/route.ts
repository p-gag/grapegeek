import { NextResponse } from 'next/server';
import { getDatabase } from '@/lib/database';

// Force this route to be static (pre-rendered at build time)
export const dynamic = 'force-static';
export const revalidate = false;

/**
 * GET /api/tree-data
 * Returns the full variety family tree graph for the interactive tree viewer.
 * This route is pre-rendered at build time for optimal performance.
 */
export async function GET() {
  try {
    const db = getDatabase();
    const treeData = db.getTreeData();
    db.close();

    return NextResponse.json(treeData);
  } catch (error) {
    console.error('Error loading tree data:', error);
    return NextResponse.json(
      { error: 'Failed to load tree data' },
      { status: 500 }
    );
  }
}
