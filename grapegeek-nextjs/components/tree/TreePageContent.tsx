'use client';

import { useState, useCallback, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  BackgroundVariant,
  useNodesState,
  useEdgesState,
  MarkerType,
  ReactFlowProvider
} from 'reactflow';
import 'reactflow/dist/style.css';
import GrapeNode from './GrapeNode';
import NodePopup from './NodePopup';
import { useTreeData } from '@/hooks/useTreeData';
import Link from 'next/link';
import { createTranslator } from '@/lib/i18n/translate';

const nodeTypes = {
  grapeNode: GrapeNode,
};

const SPECIES_COLORS: { [key: string]: string } = {
  'vinifera': 'rgba(144, 238, 144, 0.85)',
  'riparia': 'rgba(135, 206, 235, 0.85)',
  'labrusca': 'rgba(186, 85, 211, 0.85)',
  'rupestris': 'rgba(255, 160, 122, 0.85)',
  'aestivalis': 'rgba(255, 255, 0, 0.85)',
  'amurensis': 'rgba(255, 20, 147, 0.85)',
  'rotundifolia': 'rgba(147, 112, 219, 0.85)',
  'unknown': 'rgba(153, 153, 153, 0.85)'
};

interface TreePageContentInnerProps {
  initialVariety: string;
  locale: string;
}

function TreePageContentInner({ initialVariety, locale }: TreePageContentInnerProps) {
  const t = createTranslator(locale as any);
  const router = useRouter();
  const [duplicateParents, setDuplicateParents] = useState(true);
  const [colorMode, setColorMode] = useState<'species' | 'berry'>('species');
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [popupNode, setPopupNode] = useState<any>(null);
  const [popupPosition, setPopupPosition] = useState({ x: 0, y: 0 });

  const {
    treeData,
    loading,
    error,
    selectedVariety,
    setSelectedVariety,
    hoveredNodeId,
    setHoveredNodeId,
    layoutNodes,
    extractSubgraph,
    createHighlightedEdges,
    createEnhancedNodes
  } = useTreeData(initialVariety);

  // Generate tree when variety or mode changes
  const handleVarietyChange = useCallback((varietyName: string) => {
    if (!varietyName || !treeData) {
      setNodes([]);
      setEdges([]);
      return;
    }

    const subgraph = extractSubgraph(varietyName, duplicateParents);
    const layoutedNodes = layoutNodes(subgraph.nodes);
    setNodes(layoutedNodes);
    setEdges(subgraph.edges);
    setSelectedVariety(varietyName);
  }, [treeData, duplicateParents, extractSubgraph, layoutNodes, setNodes, setEdges, setSelectedVariety]);

  // Update tree when duplicate mode or initial variety changes
  useMemo(() => {
    if (initialVariety && treeData) {
      handleVarietyChange(initialVariety);
    }
  }, [initialVariety, duplicateParents, treeData, handleVarietyChange]);

  // Create highlighted edges
  const highlightedEdges = useMemo(() =>
    createHighlightedEdges(edges, hoveredNodeId),
    [edges, hoveredNodeId, createHighlightedEdges]
  );

  // Create enhanced nodes
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

  const handleNodeClick = useCallback((event: any, node: any) => {
    // Show popup at click position
    setPopupNode(node);
    setPopupPosition({ x: event.clientX, y: event.clientY });
  }, []);

  const handlePopupClose = useCallback(() => {
    setPopupNode(null);
  }, []);

  // Get current species in tree
  const currentSpecies = useMemo(() => {
    if (!nodes.length) return [];

    const speciesSet = new Set<string>();
    nodes.forEach((node: any) => {
      if (node.data.speciesComposition?.length > 0) {
        node.data.speciesComposition.forEach(({ species }: any) => {
          speciesSet.add(species);
        });
      }
    });

    const speciesOrder = ['vinifera', 'riparia', 'labrusca', 'rupestris', 'aestivalis', 'amurensis', 'rotundifolia', 'unknown'];
    return Array.from(speciesSet).sort((a, b) =>
      speciesOrder.indexOf(a) - speciesOrder.indexOf(b)
    );
  }, [nodes]);

  const getSpeciesDisplayName = (species: string) => {
    const names: { [key: string]: string } = {
      'vinifera': 'V. vinifera',
      'riparia': 'V. riparia',
      'labrusca': 'V. labrusca',
      'rupestris': 'V. rupestris',
      'aestivalis': 'V. aestivalis',
      'amurensis': 'V. amurensis',
      'rotundifolia': 'V. rotundifolia',
      'unknown': 'Unknown'
    };
    return names[species] || species;
  };

  const stats = useMemo(() => ({
    totalVarieties: treeData?.varieties.length || 0,
    totalNodes: treeData?.nodes.length || 0,
    totalEdges: treeData?.edges.length || 0,
    currentNodes: nodes.length,
    currentEdges: edges.length
  }), [nodes.length, edges.length, treeData]);

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        color: '#666',
        fontSize: '18px'
      }}>
        {t('tree.loadingData')}
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        color: '#dc3545',
        fontSize: '16px',
        padding: '20px',
        textAlign: 'center'
      }}>
        <div style={{ marginBottom: '10px' }}>❌ {t('tree.error')}</div>
        <div style={{ fontSize: '14px', color: '#666' }}>{error}</div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      {/* Sidebar */}
      <div style={{
        width: '280px',
        padding: '20px',
        background: '#f8f9fa',
        borderRight: '1px solid #dee2e6',
        overflowY: 'auto'
      }}>
        <Link
          href={`/${locale}/varieties/${encodeURIComponent(initialVariety)}`}
          style={{
            display: 'inline-block',
            marginBottom: '20px',
            color: '#8B5CF6',
            textDecoration: 'none',
            fontSize: '14px'
          }}
        >
          {t('tree.backTo', { variety: initialVariety })}
        </Link>

        <h1 style={{ fontSize: '24px', marginBottom: '10px' }}>🍇 {t('tree.subtitle')}</h1>
        <p style={{ fontSize: '14px', color: '#666', marginBottom: '20px' }}>
          {t('tree.subtitleDesc') || 'Interactive Grape Variety Explorer'}
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '15px' }}>
          <button
            style={{
              padding: '8px 12px',
              background: duplicateParents ? '#8B5CF6' : '#e9ecef',
              color: duplicateParents ? 'white' : '#333',
              border: 'none',
              borderRadius: '20px',
              cursor: 'pointer',
              fontSize: '14px'
            }}
            onClick={() => setDuplicateParents(!duplicateParents)}
          >
            🌳 {duplicateParents ? t('tree.mergedParents') : t('tree.duplicateParents')}
          </button>

          <div style={{ marginTop: '10px', fontWeight: 'bold', fontSize: '14px' }}>{t('tree.colorMode')}</div>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer', fontSize: '14px' }}>
            <input
              type="radio"
              name="colorMode"
              value="berry"
              checked={colorMode === 'berry'}
              onChange={(e) => setColorMode(e.target.value as 'berry' | 'species')}
            />
            🍇 {t('tree.berryColors')}
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer', fontSize: '14px' }}>
            <input
              type="radio"
              name="colorMode"
              value="species"
              checked={colorMode === 'species'}
              onChange={(e) => setColorMode(e.target.value as 'berry' | 'species')}
            />
            🧬 Species Colors
          </label>
        </div>

        <div style={{ fontSize: '13px', color: '#666', marginTop: '20px' }}>
          <div style={{ fontWeight: 'bold' }}>Statistics:</div>
          <div>Total varieties: {stats.totalVarieties}</div>
          <div>Total nodes: {stats.totalNodes}</div>
          <div>Total edges: {stats.totalEdges}</div>
          {selectedVariety && (
            <>
              <div>Current nodes: {stats.currentNodes}</div>
              <div>Current edges: {stats.currentEdges}</div>
            </>
          )}
        </div>

        {/* Color Legend */}
        <div style={{
          fontSize: '12px',
          color: '#666',
          marginTop: '15px',
          padding: '10px',
          background: 'rgba(248, 249, 250, 0.9)',
          border: '1px solid #ddd',
          borderRadius: '6px'
        }}>
          <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>
            {colorMode === 'species' ? '🧬 Species Colors' : '🍇 Berry Colors'}
          </div>
          {colorMode === 'species' ? (
            <div>
              {currentSpecies.map(species => (
                <div key={species} style={{ display: 'flex', alignItems: 'center', marginBottom: '3px' }}>
                  <span style={{
                    display: 'inline-block',
                    width: '16px',
                    height: '12px',
                    backgroundColor: SPECIES_COLORS[species] || SPECIES_COLORS.unknown,
                    marginRight: '6px',
                    border: '1px solid #ccc'
                  }}></span>
                  {getSpeciesDisplayName(species)}
                </div>
              ))}
            </div>
          ) : (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: '3px' }}>
                <span style={{
                  display: 'inline-block',
                  width: '16px',
                  height: '12px',
                  backgroundColor: 'rgba(240, 248, 255, 0.85)',
                  marginRight: '6px',
                  border: '1px solid #ccc'
                }}></span>
                White/Blanc
              </div>
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: '3px' }}>
                <span style={{
                  display: 'inline-block',
                  width: '16px',
                  height: '12px',
                  backgroundColor: 'rgba(255, 228, 225, 0.85)',
                  marginRight: '6px',
                  border: '1px solid #ccc'
                }}></span>
                Red/Noir
              </div>
            </div>
          )}
        </div>

        <div style={{ fontSize: '13px', color: '#888', marginTop: '20px' }}>
          💡 Click variety to explore tree | Drag to pan | Scroll to zoom
        </div>
      </div>

      {/* Tree Canvas */}
      <div style={{ flex: 1, position: 'relative' }}>
        {nodes.length > 0 ? (
          <ReactFlow
            nodes={enhancedNodes}
            edges={highlightedEdges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={handleNodeClick}
            onNodeMouseEnter={handleNodeMouseEnter}
            onNodeMouseLeave={handleNodeMouseLeave}
            nodeTypes={nodeTypes}
            fitView
            fitViewOptions={{ padding: 0.1, minZoom: 0.1, maxZoom: 1.5 }}
            minZoom={0.1}
            maxZoom={1.5}
            panOnDrag={true}
            zoomOnScroll={true}
            nodesDraggable={true}
            nodesConnectable={false}
            elementsSelectable={true}
            zoomOnDoubleClick={false}
          >
            <Controls showInteractive={false} />
            <MiniMap
              nodeStrokeWidth={3}
              nodeColor="#666"
              maskColor="rgba(255, 255, 255, 0.8)"
              pannable={true}
              zoomable={true}
            />
            <Background variant={BackgroundVariant.Dots} gap={20} size={0.5} />
          </ReactFlow>
        ) : (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            color: '#666',
            fontSize: '18px'
          }}>
            Select a grape variety to view its family tree
          </div>
        )}
      </div>

      {/* Node Popup */}
      <NodePopup
        node={popupNode}
        isVisible={!!popupNode}
        onClose={handlePopupClose}
        position={popupPosition}
        locale={locale as any}
      />
    </div>
  );
}

interface TreePageContentProps {
  initialVariety: string;
  locale?: string;
}

export default function TreePageContent({ initialVariety, locale = 'en' }: TreePageContentProps) {
  return (
    <ReactFlowProvider>
      <TreePageContentInner initialVariety={initialVariety} locale={locale} />
    </ReactFlowProvider>
  );
}
