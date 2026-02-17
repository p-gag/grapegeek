import React, { useState, useCallback, useMemo, useEffect } from 'react'
import { useParams, useNavigate, useSearchParams } from 'react-router-dom'
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  ConnectionLineType,
  MarkerType,
  ReactFlowProvider
} from 'reactflow'
import Header from '../components/Header'
import GrapeNode from '../components/GrapeNode'
import NodePopup from '../components/NodePopup'
import { useTreeData } from '../hooks/useTreeData'

// Custom node types
const nodeTypes = {
  grapeNode: GrapeNode,
}

// Default edge options - optimized for performance
const defaultEdgeOptions = {
  animated: false,
  type: 'straight', // Faster than smoothstep
  markerEnd: {
    type: MarkerType.ArrowClosed,
    color: '#999',
  },
  style: {
    stroke: '#999',
    strokeWidth: 2,
  },
}

// Species color constants from the original implementation
const SPECIES_COLORS = {
  'vinifera': 'rgba(144, 238, 144, 0.85)',  // Light green - European wine grapes
  'riparia': 'rgba(135, 206, 235, 0.85)',   // Sky blue - Cold-hardy native
  'labrusca': 'rgba(186, 85, 211, 0.85)',   // Medium orchid
  'rupestris': 'rgba(255, 160, 122, 0.85)', // Light salmon - Rock grapes
  'aestivalis': 'rgba(255, 255, 0, 0.85)',  // Yellow - Summer grapes
  'amurensis': 'rgba(255, 20, 147, 0.85)',  // Deep pink - Asian cold-hardy
  'rotundifolia': 'rgba(147, 112, 219, 0.85)', // Medium slate blue - Muscadine grapes
  'unknown': 'rgba(153, 153, 153, 0.85)'    // Gray - Unknown/unspecified
}

const TreePage = () => {
  const { variety } = useParams() // From /variety/:slug/tree routes
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  
  // Get variety from URL params or search params
  const currentVariety = variety || searchParams.get('variety')
  
  const [selectedVariety, setSelectedVariety] = useState(currentVariety || '')
  const [duplicateParents, setDuplicateParents] = useState(true)
  const [colorMode, setColorMode] = useState('species') // 'berry' or 'species'
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [popupNode, setPopupNode] = useState(null)
  const [popupPosition, setPopupPosition] = useState({ x: 0, y: 0 })
  const [hoveredNodeId, setHoveredNodeId] = useState(null)
  const [treeData, setTreeData] = useState({ varieties: [], nodes: [], edges: [] })
  const [isLoading, setIsLoading] = useState(true)
  const [loadError, setLoadError] = useState(null)

  const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), [setEdges])

  // Load tree data on component mount
  React.useEffect(() => {
    const loadTreeData = async () => {
      try {
        setIsLoading(true)
        const response = await fetch('/data/tree-data.json')
        if (!response.ok) {
          throw new Error(`Failed to load tree data: ${response.status} ${response.statusText}`)
        }
        const data = await response.json()
        setTreeData(data)
        setLoadError(null)
        
        // Check for variety URL parameter after data loads
        if (currentVariety && data.varieties.includes(currentVariety)) {
          setSelectedVariety(currentVariety)
        }
      } catch (error) {
        console.error('Error loading tree data:', error)
        setLoadError(error.message)
      } finally {
        setIsLoading(false)
      }
    }

    loadTreeData()
  }, [currentVariety])

  // Auto-layout nodes using a simple hierarchical layout
  const layoutNodes = (nodes) => {
    const levelGroups = {}
    
    // Group nodes by level
    nodes.forEach(node => {
      const level = node.data.level || 0
      if (!levelGroups[level]) {
        levelGroups[level] = []
      }
      levelGroups[level].push(node)
    })

    // Position nodes (level 0 = leftmost, higher levels = rightward)
    const layoutedNodes = []
    Object.keys(levelGroups).sort((a, b) => parseInt(a) - parseInt(b)).forEach((level, levelIndex) => {
      const levelNodes = levelGroups[level]
      levelNodes.forEach((node, nodeIndex) => {
        layoutedNodes.push({
          ...node,
          position: {
            x: levelIndex * 400, // More compact horizontal spacing
            y: nodeIndex * 150 - (levelNodes.length - 1) * 75 // Keep vertical spacing
          }
        })
      })
    })

    return layoutedNodes
  }

  // Calculate recursive species composition
  const calculateSpeciesComposition = useCallback((nodeName, edges, allNodes, visited = new Set()) => {
    // Prevent infinite loops
    if (visited.has(nodeName)) {
      return {}
    }
    visited.add(nodeName)

    // Get the node data
    const node = allNodes.find(n => n.id === nodeName)
    if (!node) return {}

    // Find parent edges for this node
    const parentEdges = edges.filter(edge => edge.target === nodeName)
    
    // If no parents, return this node's own species
    if (parentEdges.length === 0) {
      const species = node.data.species
      if (!species) return { 'unknown': 1.0 }
      
      // Normalize species name
      const speciesLower = species.toLowerCase()
      let normalizedSpecies = 'unknown'
      
      if (speciesLower.includes('vinifera')) normalizedSpecies = 'vinifera'
      else if (speciesLower.includes('riparia')) normalizedSpecies = 'riparia'
      else if (speciesLower.includes('labrusca')) normalizedSpecies = 'labrusca'
      else if (speciesLower.includes('rupestris')) normalizedSpecies = 'rupestris'
      else if (speciesLower.includes('aestivalis') || speciesLower.includes('lincecumii')) normalizedSpecies = 'aestivalis'
      else if (speciesLower.includes('amurensis')) normalizedSpecies = 'amurensis'
      else if (speciesLower.includes('rotundifolia') || speciesLower.includes('muscadinia')) normalizedSpecies = 'rotundifolia'
      
      return { [normalizedSpecies]: 1.0 }
    }

    // Recursively get parent compositions
    const parentCompositions = parentEdges.map(edge => {
      const parentName = edge.source.split('#')[0] // Remove duplicate suffix
      return calculateSpeciesComposition(parentName, edges, allNodes, new Set(visited))
    })

    // Average the parent compositions (each parent contributes equally)
    const combinedComposition = {}
    const contributionPerParent = 1.0 / parentCompositions.length

    parentCompositions.forEach(composition => {
      Object.entries(composition).forEach(([species, proportion]) => {
        if (!combinedComposition[species]) {
          combinedComposition[species] = 0
        }
        combinedComposition[species] += proportion * contributionPerParent
      })
    })

    return combinedComposition
  }, [])

  // Extract subgraph for selected variety
  const extractSubgraph = useCallback((varietyName, duplicateMode = false) => {
    if (!varietyName || !treeData.varieties.includes(varietyName)) {
      return { nodes: [], edges: [] }
    }

    const subgraphNodes = new Set()
    const subgraphEdges = []
    const nodeCounter = {}

    // Get unique node ID for duplication mode
    const getUniqueId = (nodeName, forceNew = false) => {
      if (!duplicateMode && !forceNew) return nodeName
      
      // Always increment counter for new instances
      if (!nodeCounter[nodeName]) {
        nodeCounter[nodeName] = 1
        return `${nodeName}#1`
      }
      nodeCounter[nodeName]++
      return `${nodeName}#${nodeCounter[nodeName]}`
    }

    // Recursively collect ancestors
    const collectAncestors = (nodeName, visited = new Set(), path = '', isRoot = false) => {
      // In merged mode (not duplicate), check for already visited
      if (!duplicateMode && visited.has(nodeName)) return nodeName // Return existing node ID
      if (!duplicateMode) visited.add(nodeName)

      // For the root node, never duplicate. For others, create unique IDs in duplicate mode
      const uniqueId = isRoot ? nodeName : getUniqueId(nodeName, duplicateMode)
      subgraphNodes.add(uniqueId)

      // Find parent edges
      const parentEdges = treeData.edges.filter(edge => edge.target === nodeName)
      
      parentEdges.forEach((edge, index) => {
        let parentUniqueId
        
        if (duplicateMode) {
          // In duplicate mode, each parent reference gets its own tree
          parentUniqueId = collectAncestors(edge.source, new Set(), `${path}/p${index}`, false)
        } else {
          // In merged mode, share the same parent instances
          parentUniqueId = collectAncestors(edge.source, visited, path, false)
        }
        
        if (parentUniqueId) {
          subgraphEdges.push({
            ...edge,
            id: `${parentUniqueId}->${uniqueId}`,
            source: parentUniqueId,
            target: uniqueId
          })
        }
      })

      return uniqueId
    }

    // Start from selected variety
    collectAncestors(varietyName, new Set(), '', true)

    // Create nodes with proper data and positioning
    const nodes = Array.from(subgraphNodes).map(nodeId => {
      const originalName = nodeId.split('#')[0]
      const originalNode = treeData.nodes.find(n => n.id === originalName)
      
      if (!originalNode) return null

      // Calculate recursive species composition
      const speciesComposition = calculateSpeciesComposition(originalName, treeData.edges, treeData.nodes)
      
      // Convert composition to sorted array for color bar
      const speciesArray = Object.entries(speciesComposition)
        .sort(([,a], [,b]) => b - a) // Sort by proportion descending
        .map(([species, proportion]) => ({ species, proportion }))

      return {
        ...originalNode,
        id: nodeId,
        type: 'grapeNode',
        data: {
          ...originalNode.data,
          is_selected: originalName === varietyName && !nodeId.includes('#'),
          is_duplicate: nodeId.includes('#'),
          colorMode: colorMode,
          speciesComposition: speciesArray,
          is_hovered: hoveredNodeId && hoveredNodeId.split('#')[0] === originalName
        }
      }
    }).filter(Boolean)

    // Calculate hierarchical levels
    const levels = calculateLevels(nodes, subgraphEdges, varietyName)
    
    // Apply levels to nodes
    nodes.forEach(node => {
      node.data.level = levels[node.id] || 0
    })

    return { nodes, edges: subgraphEdges }
  }, [calculateSpeciesComposition, colorMode, hoveredNodeId, treeData])

  // Calculate hierarchical levels
  const calculateLevels = useCallback((nodes, edges, selectedVariety) => {
    const levels = {}
    const childrenOf = {}
    const parentsOf = {}

    // Build adjacency lists
    edges.forEach(edge => {
      if (!childrenOf[edge.source]) childrenOf[edge.source] = []
      if (!parentsOf[edge.target]) parentsOf[edge.target] = []
      childrenOf[edge.source].push(edge.target)
      parentsOf[edge.target].push(edge.source)
    })

    // Initialize levels
    nodes.forEach(node => {
      levels[node.id] = 0
    })

    // Set selected variety at level 0
    levels[selectedVariety] = 0

    // Calculate parent levels
    let changed = true
    let iterations = 0
    while (changed && iterations < 20) {
      changed = false
      iterations++

      Object.keys(levels).forEach(nodeId => {
        if (parentsOf[nodeId]) {
          const currentLevel = levels[nodeId]
          const requiredParentLevel = currentLevel + 1
          
          parentsOf[nodeId].forEach(parent => {
            if (levels[parent] < requiredParentLevel) {
              levels[parent] = requiredParentLevel
              changed = true
            }
          })
        }
      })
    }

    return levels
  }, [])

  // Create edges with hover highlighting
  const highlightedEdges = useMemo(() => {
    if (!hoveredNodeId) return edges
    
    const hoveredOriginalName = hoveredNodeId.split('#')[0]
    
    return edges.map(edge => {
      const sourceOriginalName = edge.source.split('#')[0]
      const targetOriginalName = edge.target.split('#')[0]
      const isConnectedToHovered = sourceOriginalName === hoveredOriginalName || targetOriginalName === hoveredOriginalName
      
      return {
        ...edge,
        style: {
          ...edge.style,
          stroke: isConnectedToHovered ? '#007bff' : '#999',
          strokeWidth: isConnectedToHovered ? 3 : 2,
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: isConnectedToHovered ? '#007bff' : '#999',
        }
      }
    })
  }, [edges, hoveredNodeId])

  const handleVarietyChange = useCallback((varietyName) => {
    if (!varietyName) {
      setNodes([])
      setEdges([])
      setSelectedVariety('')
      return
    }

    const subgraph = extractSubgraph(varietyName, duplicateParents)
    
    // Layout nodes and set them
    const layoutedNodes = layoutNodes(subgraph.nodes)
    setNodes(layoutedNodes)
    setEdges(subgraph.edges)
    setSelectedVariety(varietyName)
  }, [setNodes, setEdges, duplicateParents, extractSubgraph])

  const handleNodeMouseEnter = useCallback((event, node) => {
    if (node && node.id) {
      setHoveredNodeId(node.id)
    }
  }, [])

  const handleNodeMouseLeave = useCallback(() => {
    setHoveredNodeId(null)
  }, [])

  const handleNodeClick = useCallback((event, node) => {
    const originalName = node.id.split('#')[0] // Remove duplicate suffix
    
    if (event.detail === 2) {
      // Double-click to switch to a different variety
      if (treeData.varieties.includes(originalName)) {
        handleVarietyChange(originalName)
        setPopupNode(null) // Close popup when navigating
      }
    } else {
      // Single-click to show popup
      setPopupNode(node)
      setPopupPosition({ 
        x: event.clientX || window.innerWidth / 2, 
        y: event.clientY || window.innerHeight / 2 
      })
    }
  }, [handleVarietyChange, treeData.varieties])

  const handleClosePopup = useCallback(() => {
    setPopupNode(null)
  }, [])

  // Re-render tree when duplicate mode or color mode changes
  React.useEffect(() => {
    if (selectedVariety && treeData.varieties?.length > 0) {
      handleVarietyChange(selectedVariety)
    }
  }, [duplicateParents, colorMode, selectedVariety, treeData, handleVarietyChange])

  // Get all unique species in current tree
  const currentSpecies = useMemo(() => {
    if (!nodes.length) return []
    
    const speciesSet = new Set()
    nodes.forEach(node => {
      if (node.data.speciesComposition?.length > 0) {
        node.data.speciesComposition.forEach(({ species }) => {
          speciesSet.add(species)
        })
      } else if (node.data.species) {
        // Normalize species name like in the composition calculation
        const speciesLower = node.data.species.toLowerCase()
        let normalizedSpecies = 'unknown'
        
        if (speciesLower.includes('vinifera')) normalizedSpecies = 'vinifera'
        else if (speciesLower.includes('riparia')) normalizedSpecies = 'riparia'
        else if (speciesLower.includes('labrusca')) normalizedSpecies = 'labrusca'
        else if (speciesLower.includes('rupestris')) normalizedSpecies = 'rupestris'
        else if (speciesLower.includes('aestivalis') || speciesLower.includes('lincecumii')) normalizedSpecies = 'aestivalis'
        else if (speciesLower.includes('amurensis')) normalizedSpecies = 'amurensis'
        else if (speciesLower.includes('rotundifolia') || speciesLower.includes('muscadinia')) normalizedSpecies = 'rotundifolia'
        
        speciesSet.add(normalizedSpecies)
      }
    })
    
    // Sort species by commonality (vinifera first, unknown last)
    const speciesOrder = ['vinifera', 'riparia', 'labrusca', 'rupestris', 'aestivalis', 'amurensis', 'rotundifolia', 'unknown']
    return Array.from(speciesSet).sort((a, b) => {
      return speciesOrder.indexOf(a) - speciesOrder.indexOf(b)
    })
  }, [nodes])

  // Get display name for species
  const getSpeciesDisplayName = useCallback((species) => {
    const names = {
      'vinifera': 'V. vinifera',
      'riparia': 'V. riparia', 
      'labrusca': 'V. labrusca',
      'rupestris': 'V. rupestris',
      'aestivalis': 'V. aestivalis',
      'amurensis': 'V. amurensis',
      'rotundifolia': 'V. rotundifolia',
      'unknown': 'Unknown'
    }
    return names[species] || species
  }, [])

  // Statistics
  const stats = useMemo(() => {
    return {
      totalVarieties: treeData.varieties.length,
      totalNodes: treeData.nodes.length,
      totalEdges: treeData.edges.length,
      currentNodes: nodes.length,
      currentEdges: edges.length
    }
  }, [nodes.length, edges.length, treeData])

  const handleBackClick = () => {
    if (currentVariety) {
      const varietySlug = currentVariety.toLowerCase().replace(/\s+/g, '-')
      navigate(`/variety/${varietySlug}`)
    } else {
      navigate(-1)
    }
  }

  return (
    <div className="app">
      <Header showBackLink={true} />
      
      <div className="tree-page">
        <div className="tree-sidebar">
          <h1>🍇 Grape Family Trees</h1>
          <p style={{ fontSize: '14px', color: '#666', marginBottom: '20px' }}>
            Interactive Grape Variety Explorer
          </p>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '15px' }}>
            <button 
              style={{
                padding: '6px 12px',
                background: duplicateParents ? 'var(--brand-accent)' : '#e9ecef',
                color: duplicateParents ? 'white' : '#333',
                border: 'none',
                borderRadius: '20px',
                cursor: 'pointer',
                fontSize: '14px',
                transition: 'background-color 0.2s'
              }}
              onClick={() => setDuplicateParents(!duplicateParents)}
            >
              🌳 Duplicate Parents
            </button>
            
            <div style={{ marginBottom: '10px', fontWeight: 'bold' }}>Color Mode:</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
                <input 
                  type="radio" 
                  name="colorMode" 
                  value="berry"
                  checked={colorMode === 'berry'}
                  onChange={(e) => setColorMode(e.target.value)}
                />
                🍇 Berry Colors
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
                <input 
                  type="radio" 
                  name="colorMode" 
                  value="species"
                  checked={colorMode === 'species'}
                  onChange={(e) => setColorMode(e.target.value)}
                />
                🧬 Species Colors
              </label>
            </div>
          </div>

          <div style={{ fontSize: '14px', color: '#666', marginTop: '20px' }}>
            <div><strong>Statistics:</strong></div>
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
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '3px' }}>
                  <span style={{ 
                    display: 'inline-block', 
                    width: '16px', 
                    height: '12px', 
                    backgroundColor: 'rgba(255, 238, 240, 0.85)',
                    marginRight: '6px',
                    border: '1px solid #ccc'
                  }}></span>
                  Pink/Rose
                </div>
              </div>
            )}
          </div>

          <div style={{ fontSize: '13px', color: '#888', marginTop: '20px' }}>
            💡 Click variety to explore tree | Drag to pan | Scroll to zoom
          </div>
        </div>

        <div className="tree-content">
          <div className="tree-flow-container">
            {isLoading ? (
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                height: '100%',
                color: '#666',
                fontSize: '18px'
              }}>
                Loading grape variety data...
              </div>
            ) : loadError ? (
              <div style={{ 
                display: 'flex', 
                flexDirection: 'column',
                alignItems: 'center', 
                justifyContent: 'center', 
                height: '100%',
                color: '#dc3545',
                fontSize: '16px',
                padding: '20px',
                textAlign: 'center'
              }}>
                <div style={{ marginBottom: '10px' }}>❌ Error loading data</div>
                <div style={{ fontSize: '14px', color: '#666' }}>{loadError}</div>
              </div>
            ) : selectedVariety ? (
              <ReactFlowProvider>
                <ReactFlow
                  nodes={nodes}
                  edges={highlightedEdges}
                  onNodesChange={onNodesChange}
                  onEdgesChange={onEdgesChange}
                  onConnect={onConnect}
                  onNodeClick={handleNodeClick}
                  onNodeMouseEnter={handleNodeMouseEnter}
                  onNodeMouseLeave={handleNodeMouseLeave}
                  nodeTypes={nodeTypes}
                  defaultEdgeOptions={defaultEdgeOptions}
                  connectionLineType={ConnectionLineType.SmoothStep}
                  fitView
                  fitViewOptions={{ padding: 0.1, minZoom: 0.1, maxZoom: 1.5 }}
                  minZoom={0.1}
                  maxZoom={1.5}
                  panOnScroll={false}
                  panOnScrollMode="free"
                  panOnDrag={true}
                  zoomOnScroll={true}
                  zoomOnPinch={true}
                  preventScrolling={false}
                  nodesDraggable={true}
                  nodesConnectable={false}
                  elementsSelectable={true}
                  zoomOnDoubleClick={false}
                  selectNodesOnDrag={false}
                  deleteKeyCode={null}
                >
                  <Controls showInteractive={false} />
                  <MiniMap 
                    nodeStrokeWidth={3}
                    nodeColor="#666"
                    maskColor="rgba(255, 255, 255, 0.8)"
                    pannable={true}
                    zoomable={true}
                  />
                  <Background variant="dots" gap={20} size={0.5} />
                </ReactFlow>
              </ReactFlowProvider>
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
        </div>
      </div>
      
      {/* Node Popup */}
      <NodePopup 
        node={popupNode}
        isVisible={!!popupNode}
        onClose={handleClosePopup}
        position={popupPosition}
      />
    </div>
  )
}

export default TreePage