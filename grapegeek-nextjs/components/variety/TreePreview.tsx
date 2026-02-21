'use client';

import Link from 'next/link';
import type { GrapeVariety } from '@/lib/types';

interface TreePreviewProps {
  variety: GrapeVariety;
}

export default function TreePreview({ variety }: TreePreviewProps) {
  const hasParents = variety.parent1_name || variety.parent2_name;
  const hasParent1 = Boolean(variety.parent1_name);
  const hasParent2 = Boolean(variety.parent2_name);

  return (
    <div className="preview-section">
      <div className="preview-header">
        <h2>🌳 Family Tree</h2>
        <p>Genetic origins and parentage of {variety.name}</p>
      </div>

      <div className="tree-preview-container">
        <div className="tree-rectangle">
          {hasParents ? (
            <div className="simple-tree">
              {/* Parents Row */}
              <div className="tree-parents">
                {hasParent1 && (
                  <div className="tree-node parent">
                    <div className="node-content">{variety.parent1_name}</div>
                  </div>
                )}
                {hasParent1 && hasParent2 && (
                  <div className="tree-cross">×</div>
                )}
                {hasParent2 && (
                  <div className="tree-node parent">
                    <div className="node-content">{variety.parent2_name}</div>
                  </div>
                )}
              </div>

              {/* Connecting Line */}
              <div className="tree-connector" />

              {/* Current Variety */}
              <div className="tree-current">
                <div className="tree-node current">
                  <div className="node-content">{variety.name}</div>
                </div>
              </div>
            </div>
          ) : (
            <div className="tree-placeholder">
              <p>Parent information not available</p>
            </div>
          )}

          <div className="tree-invitation">
            <div className="invitation-text">Explore interactive family tree</div>
            <div className="invitation-arrow">→</div>
          </div>
        </div>

        <Link
          href={`/tree?variety=${encodeURIComponent(variety.name)}`}
          className="tree-overlay-button"
          aria-label="Open interactive family tree"
        >
          <span className="sr-only">Open Interactive Family Tree</span>
        </Link>
      </div>
    </div>
  );
}
