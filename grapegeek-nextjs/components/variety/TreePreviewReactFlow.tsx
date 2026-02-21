'use client';

import { useEffect, useMemo, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import ReactFlow, {
  Background,
  useNodesState,
  useEdgesState,
  ReactFlowProvider,
  useReactFlow
} from 'reactflow';
import 'reactflow/dist/style.css';
import GrapeNode from '../tree/GrapeNode';
import { useTreeData } from '@/hooks/useTreeData';
import type { GrapeVariety } from '@/lib/types';
import type { Locale } from '@/lib/i18n/config';

const nodeTypes = {
  grapeNode: GrapeNode
};

interface TreePreviewContentProps {
  variety: GrapeVariety;
  locale: Locale;
}

const TreePreviewContent = ({ variety, locale }: TreePreviewContentProps) => {
  const router = useRouter();
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const { fitView } = useReactFlow();
  const containerRef = useRef<HTMLDivElement>(null);

  const {
    loading,
    error,
    hoveredNodeId,
    setHoveredNodeId,
    layoutNodes,
    extractSubgraph,
    createHighlightedEdges,
    createEnhancedNodes
  } = useTreeData(variety.name);

  // Generate tree when variety changes
  useEffect(() => {
    const subgraph = extractSubgraph(variety.name, true);
    if (subgraph.nodes.length > 0) {
      const layoutedNodes = layoutNodes(subgraph.nodes);
      setNodes(layoutedNodes);
      setEdges(subgraph.edges);
    }
  }, [variety.name, extractSubgraph, layoutNodes, setNodes, setEdges]);

  // Fit view when nodes change or container resizes
  useEffect(() => {
    if (nodes.length > 0) {
      const handleResize = () => {
        fitView({ padding: 0.25, minZoom: 0.1, maxZoom: 1, duration: 200 });
      };

      // Initial fit
      const initialTimer = setTimeout(handleResize, 100);

      // Watch for window resize
      window.addEventListener('resize', handleResize);

      // Watch for container size changes using ResizeObserver
      let resizeObserver: ResizeObserver | undefined;
      if (containerRef.current) {
        resizeObserver = new ResizeObserver(handleResize);
        resizeObserver.observe(containerRef.current);
      }

      return () => {
        clearTimeout(initialTimer);
        window.removeEventListener('resize', handleResize);
        if (resizeObserver) {
          resizeObserver.disconnect();
        }
      };
    }
  }, [nodes, fitView]);

  // Create highlighted edges and enhanced nodes
  const highlightedEdges = useMemo(() =>
    createHighlightedEdges(edges, hoveredNodeId),
    [edges, hoveredNodeId, createHighlightedEdges]
  );

  const enhancedNodes = useMemo(() =>
    createEnhancedNodes(nodes, hoveredNodeId),
    [nodes, hoveredNodeId, createEnhancedNodes]
  );

  const handleNodeMouseEnter = useCallback((_event: any, node: any) => {
    if (node && node.id) {
      setHoveredNodeId(node.id);
    }
  }, [setHoveredNodeId]);

  const handleNodeMouseLeave = useCallback(() => {
    setHoveredNodeId(null);
  }, [setHoveredNodeId]);

  const handleOpenFullTree = () => {
    router.push(`/${locale}/tree?variety=${encodeURIComponent(variety.name)}`);
  };

  if (loading) {
    return (
      <div className="preview-section">
        <div className="preview-header">
          <h2>🌳 Family Tree</h2>
          <p>Genetic origins and parentage of {variety.name}</p>
        </div>
        <div className="tree-preview-container">
          <div className="tree-rectangle" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div>Loading family tree...</div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="preview-section">
        <div className="preview-header">
          <h2>🌳 Family Tree</h2>
          <p>Genetic origins and parentage of {variety.name}</p>
        </div>
        <div className="tree-preview-container">
          <div className="tree-rectangle" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div>Error loading tree: {error}</div>
          </div>
        </div>
      </div>
    );
  }

  if (nodes.length === 0) {
    return (
      <div className="preview-section">
        <div className="preview-header">
          <h2>🌳 Family Tree</h2>
          <p>Genetic origins and parentage of {variety.name}</p>
        </div>
        <div className="tree-preview-container">
          <div className="tree-rectangle" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div>No family tree data available for {variety.name}</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="preview-section">
      <div className="preview-header">
        <h2>🌳 Family Tree</h2>
        <p>Genetic origins and parentage of {variety.name}</p>
      </div>

      <div className="tree-preview-container">
        <div className="tree-rectangle" ref={containerRef}>
          <ReactFlow
            nodes={enhancedNodes}
            edges={highlightedEdges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeMouseEnter={handleNodeMouseEnter}
            onNodeMouseLeave={handleNodeMouseLeave}
            nodeTypes={nodeTypes}
            fitView
            fitViewOptions={{ padding: 0.25, minZoom: 0.1, maxZoom: 1 }}
            minZoom={0.1}
            maxZoom={1.5}
            zoomOnScroll={false}
            zoomOnPinch={false}
            zoomOnDoubleClick={false}
            panOnDrag={false}
            elementsSelectable={false}
            nodesDraggable={false}
            nodesConnectable={false}
            style={{ borderRadius: '16px', width: '100%', height: '100%' }}
          >
            <Background />
          </ReactFlow>

          <div className="tree-invitation">
            <div className="invitation-text">
              Explore interactive family tree
            </div>
            <div className="invitation-arrow">→</div>
          </div>
        </div>

        <button
          className="tree-overlay-button"
          onClick={handleOpenFullTree}
          aria-label="Open interactive family tree"
        >
          <span className="sr-only">Open Interactive Family Tree</span>
        </button>
      </div>
    </div>
  );
};

interface TreePreviewReactFlowProps {
  variety: GrapeVariety;
  locale: Locale;
}

const TreePreviewReactFlow = ({ variety, locale }: TreePreviewReactFlowProps) => {
  return (
    <ReactFlowProvider>
      <TreePreviewContent variety={variety} locale={locale} />
    </ReactFlowProvider>
  );
};

export default TreePreviewReactFlow;
