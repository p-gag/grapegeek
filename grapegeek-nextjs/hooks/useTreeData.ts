import { useState, useEffect, useCallback, useMemo } from 'react';
import { MarkerType } from 'reactflow';

interface TreeNode {
  id: string;
  type?: string;
  position: { x: number; y: number };
  data: any;
}

interface TreeEdge {
  id: string;
  source: string;
  target: string;
  type?: string;
  style?: any;
  markerEnd?: any;
}

interface TreeData {
  nodes: any[];
  edges: any[];
  varieties: string[];
}

interface SpeciesComposition {
  [species: string]: number;
}

export const useTreeData = (initialVariety: string = '') => {
  const [treeData, setTreeData] = useState<TreeData | null>(null);
  const [selectedVariety, setSelectedVariety] = useState(initialVariety);
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Layout nodes function
  const layoutNodes = useCallback((nodes: TreeNode[]) => {
    const levelGroups: { [key: number]: TreeNode[] } = {};

    // Group nodes by level
    nodes.forEach(node => {
      const level = node.data.level || 0;
      if (!levelGroups[level]) {
        levelGroups[level] = [];
      }
      levelGroups[level].push(node);
    });

    // Position nodes (level 0 = leftmost, higher levels = rightward)
    const layoutedNodes: TreeNode[] = [];
    Object.keys(levelGroups).sort((a, b) => parseInt(a) - parseInt(b)).forEach((level, levelIndex) => {
      const levelNodes = levelGroups[parseInt(level)];
      levelNodes.forEach((node, nodeIndex) => {
        layoutedNodes.push({
          ...node,
          position: {
            x: levelIndex * 400, // More compact horizontal spacing
            y: nodeIndex * 180 - (levelNodes.length - 1) * 90 // Increased vertical spacing for 3-line names
          }
        });
      });
    });

    return layoutedNodes;
  }, []);

  // Calculate recursive species composition
  const calculateSpeciesComposition = useCallback((nodeName: string, edges: any[], allNodes: any[], visited: Set<string> = new Set()): SpeciesComposition => {
    if (visited.has(nodeName)) {
      return {};
    }
    visited.add(nodeName);

    const node = allNodes.find(n => n.id === nodeName);
    if (!node) return {};

    const parentEdges = edges.filter(edge => edge.target === nodeName);

    if (parentEdges.length === 0) {
      const species = node.data.species;
      if (!species) return { 'unknown': 1.0 };

      const speciesLower = species.toLowerCase();
      let normalizedSpecies = 'unknown';

      if (speciesLower.includes('vinifera')) normalizedSpecies = 'vinifera';
      else if (speciesLower.includes('riparia')) normalizedSpecies = 'riparia';
      else if (speciesLower.includes('labrusca')) normalizedSpecies = 'labrusca';
      else if (speciesLower.includes('rupestris')) normalizedSpecies = 'rupestris';
      else if (speciesLower.includes('aestivalis') || speciesLower.includes('lincecumii')) normalizedSpecies = 'aestivalis';
      else if (speciesLower.includes('amurensis')) normalizedSpecies = 'amurensis';
      else if (speciesLower.includes('rotundifolia') || speciesLower.includes('muscadinia')) normalizedSpecies = 'rotundifolia';

      return { [normalizedSpecies]: 1.0 };
    }

    const parentCompositions = parentEdges.map(edge => {
      const parentName = edge.source.split('#')[0];
      return calculateSpeciesComposition(parentName, edges, allNodes, new Set(visited));
    });

    const combinedComposition: SpeciesComposition = {};
    // Each parent always contributes 50%, regardless of how many parents we have data for
    const contributionPerParent = 0.5;

    parentCompositions.forEach(composition => {
      Object.entries(composition).forEach(([species, proportion]) => {
        if (!combinedComposition[species]) {
          combinedComposition[species] = 0;
        }
        combinedComposition[species] += proportion * contributionPerParent;
      });
    });

    // If we have fewer than 2 parents with data, add unknown species for missing parents
    if (parentCompositions.length < 2) {
      const unknownContribution = (2 - parentCompositions.length) * 0.5;
      if (!combinedComposition['unknown']) {
        combinedComposition['unknown'] = 0;
      }
      combinedComposition['unknown'] += unknownContribution;
    }

    return combinedComposition;
  }, []);

  // Calculate levels
  const calculateLevels = useCallback((nodes: string[], edges: TreeEdge[], selectedVariety: string) => {
    const levels: { [key: string]: number } = {};
    const childrenOf: { [key: string]: string[] } = {};
    const parentsOf: { [key: string]: string[] } = {};

    nodes.forEach(nodeId => {
      childrenOf[nodeId] = [];
      parentsOf[nodeId] = [];
    });

    edges.forEach(edge => {
      if (!childrenOf[edge.source]) childrenOf[edge.source] = [];
      if (!parentsOf[edge.target]) parentsOf[edge.target] = [];
      childrenOf[edge.source].push(edge.target);
      parentsOf[edge.target].push(edge.source);
    });

    nodes.forEach(node => {
      levels[node] = 0;
    });

    levels[selectedVariety] = 0;

    let changed = true;
    let iterations = 0;
    while (changed && iterations < 20) {
      changed = false;
      iterations++;

      Object.keys(levels).forEach(nodeId => {
        if (parentsOf[nodeId]) {
          const currentLevel = levels[nodeId];
          const requiredParentLevel = currentLevel + 1;

          parentsOf[nodeId].forEach(parent => {
            if (levels[parent] < requiredParentLevel) {
              levels[parent] = requiredParentLevel;
              changed = true;
            }
          });
        }
      });
    }

    return levels;
  }, []);

  // Extract subgraph for selected variety
  const extractSubgraph = useCallback((varietyName: string, duplicateMode: boolean = false): { nodes: TreeNode[], edges: TreeEdge[] } => {
    if (!varietyName || !treeData || !treeData.varieties.includes(varietyName)) {
      return { nodes: [], edges: [] };
    }

    const subgraphNodes = new Set<string>();
    const subgraphEdges: TreeEdge[] = [];
    const nodeCounter: { [key: string]: number } = {};
    const visited = new Set<string>(); // Global visited set for non-duplicate mode

    const getUniqueId = (nodeName: string, forceNew: boolean = false): string => {
      if (!duplicateMode && !forceNew) return nodeName;

      if (!nodeCounter[nodeName]) {
        nodeCounter[nodeName] = 0;
      }

      if (forceNew || nodeCounter[nodeName] > 0) {
        nodeCounter[nodeName]++;
        return `${nodeName}#${nodeCounter[nodeName]}`;
      }

      nodeCounter[nodeName]++;
      return nodeName;
    };

    const traverse = (nodeName: string, depth: number = 0, maxDepth: number = 10, isRoot: boolean = false): string => {
      if (depth > maxDepth) return nodeName;

      // For the root node, never duplicate. For others, create unique IDs in duplicate mode
      const uniqueId = isRoot ? nodeName : getUniqueId(nodeName, duplicateMode);

      // In merged mode (not duplicate), check for already visited nodes
      if (!duplicateMode && !isRoot && visited.has(nodeName)) {
        return nodeName; // Return existing node ID (without suffix)
      }
      if (!duplicateMode && !isRoot) {
        visited.add(nodeName);
      }

      subgraphNodes.add(uniqueId);

      const parentEdges = treeData.edges.filter((edge: any) => edge.target === nodeName);
      parentEdges.forEach((edge: any) => {
        const parentName = edge.source;

        if (duplicateMode) {
          // In duplicate mode, each parent reference gets its own tree
          const parentUniqueId = traverse(parentName, depth + 1, maxDepth, false);

          subgraphEdges.push({
            id: `${parentUniqueId}-${uniqueId}`,
            source: parentUniqueId,
            target: uniqueId,
            type: 'default',
            style: { stroke: '#999', strokeWidth: 2 },
            markerEnd: { type: MarkerType.ArrowClosed, color: '#999' }
          });
        } else {
          // In merged mode, reuse existing parent nodes
          const parentUniqueId = traverse(parentName, depth + 1, maxDepth, false) || parentName;

          subgraphEdges.push({
            id: `${parentUniqueId}-${uniqueId}`,
            source: parentUniqueId,
            target: uniqueId,
            type: 'default',
            style: { stroke: '#999', strokeWidth: 2 },
            markerEnd: { type: MarkerType.ArrowClosed, color: '#999' }
          });
        }
      });

      return uniqueId;
    };

    traverse(varietyName, 0, 10, true);

    const levels = calculateLevels(Array.from(subgraphNodes), subgraphEdges, varietyName);

    const processedNodes = Array.from(subgraphNodes).map(nodeId => {
      const originalName = nodeId.split('#')[0];
      const originalNode = treeData.nodes.find((n: any) => n.id === originalName);

      if (!originalNode) {
        return null;
      }

      const speciesComposition = calculateSpeciesComposition(originalName, treeData.edges, treeData.nodes);
      const speciesArray = Object.entries(speciesComposition)
        .filter(([_, proportion]) => proportion > 0)
        .sort(([,a], [,b]) => b - a)
        .map(([species, proportion]) => ({ species, proportion }));

      return {
        id: nodeId,
        type: 'grapeNode',
        position: { x: 0, y: 0 },
        data: {
          ...originalNode.data,
          is_selected: originalName === varietyName,
          is_duplicate: nodeId !== originalName,
          colorMode: 'species',
          speciesComposition: speciesArray,
          level: levels[nodeId] || 0
        }
      };
    }).filter(Boolean) as TreeNode[];

    return { nodes: processedNodes, edges: subgraphEdges };
  }, [treeData, calculateSpeciesComposition, calculateLevels]);

  // Create edges with hover highlighting
  const createHighlightedEdges = useCallback((edges: TreeEdge[], hoveredNodeId: string | null): TreeEdge[] => {
    if (!hoveredNodeId) return edges;

    const hoveredOriginalName = hoveredNodeId.split('#')[0];

    return edges.map(edge => {
      const sourceOriginalName = edge.source.split('#')[0];
      const targetOriginalName = edge.target.split('#')[0];
      const isConnectedToHovered = sourceOriginalName === hoveredOriginalName || targetOriginalName === hoveredOriginalName;

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
      };
    });
  }, []);

  // Enhanced nodes with hover state
  const createEnhancedNodes = useCallback((nodes: TreeNode[], hoveredNodeId: string | null): TreeNode[] => {
    if (!hoveredNodeId) return nodes;

    const hoveredOriginalName = hoveredNodeId.split('#')[0];

    return nodes.map(node => {
      const nodeOriginalName = node.id.split('#')[0];
      return {
        ...node,
        data: {
          ...node.data,
          is_hovered: nodeOriginalName === hoveredOriginalName
        }
      };
    });
  }, []);

  // Load tree data
  useEffect(() => {
    const loadTreeData = async () => {
      try {
        setLoading(true);
        const response = await fetch('/data/tree-data.json');
        if (!response.ok) {
          throw new Error(`Failed to load tree data: ${response.status}`);
        }
        const data = await response.json();
        setTreeData(data);
      } catch (err: any) {
        console.error('Error loading tree data:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadTreeData();
  }, []);

  // Update selected variety
  useEffect(() => {
    setSelectedVariety(initialVariety);
  }, [initialVariety]);

  return {
    // State
    treeData,
    selectedVariety,
    hoveredNodeId,
    loading,
    error,

    // Actions
    setSelectedVariety,
    setHoveredNodeId,

    // Functions
    layoutNodes,
    extractSubgraph,
    createHighlightedEdges,
    createEnhancedNodes,
    calculateSpeciesComposition
  };
};
