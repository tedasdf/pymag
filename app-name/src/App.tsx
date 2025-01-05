import {React , useState} from 'react';
import { ReactFlow, useNodesState, useEdgesState, Background, MiniMap, Controls } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import fetchAndCreateNodes from './utils/helper'
import FunctionNode from './components/nodes/FunctionNode';

const initialNodes: any[] = [];

const initialEdges: any[] = [];


const nodeType = {
  "functionNode": FunctionNode,
}

// const edgeType = {
//   // "variablePointsToEdge" : VariablePointsToEdge;
//   // "Function flow": 
// };

const defaultViewport = { x: 0, y: 0, zoom: 1.5 };



const HoverEffectNodes = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges,, onEdgesChange] = useEdgesState(initialEdges);
  const [isButtonVisible, setButtonVisible] = useState(true); // Add state for button visibility
  
  const startseq = async () => {
    setButtonVisible(false);
    console.log("Trigger useEffect");
    let newNode = await fetchAndCreateNodes(nodes);
    console.log("This is newNode ")
    console.log(newNode);
    if (newNode) {
      await setNodes((nds) => [...nds, ...newNode]); // Append new nodes to existing nodes
    }
  };

 
  
  const onNodeClick = (event: React.MouseEvent, node: any) => {
    console.log("NOdes");
    console.log(nodes);
  }
  //   setNodes((nds) =>
  //     nds.map((n) => {
  //       if (n.id === node.id) {
  //         // Toggle type and size for the parent node
  //         const newType = n.type === 'default' ? 'group' : 'default';
  //         const newWidth = n.style.width === 150 ? 100 : 250;
  //         const newHeight = n.style.height === 75 ? 50 : 500;

  //         return {
  //           ...n,
  //           type: newType,
  //           style: {
  //             ...n.style,
  //             width: newWidth,
  //             height: newHeight,
  //           },
  //         };
  //       }

  //       if (n.parentId === node.id) {
  //         // Toggle visibility for the sub-node
  //         return {
  //           ...n,
  //           style: {
  //             ...n.style,
  //             display: n.style.display === 'block' ? 'none' : 'block',
  //           },
  //         };
  //       }

  //       // Return unchanged nodes
  //       return n;
  //     })
  //   );
  // };

  return (
    <>
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onNodeClick={onNodeClick}
      defaultViewport={defaultViewport}
      minZoom={0.2}
      style={{ background: '#F7F9FB' }}
      maxZoom={4}
      fitView
    >
      <Background />
      <Controls />
      <MiniMap 
        nodeColor={(node) => {
          return node.style?.backgroundColor || '#eee';
        }}
        zoomable 
        pannable 
      />
    </ReactFlow>
    {isButtonVisible && <button 
    onClick={startseq}
    style={{ position: 'absolute', top: '20px', left: '20px', zIndex: 10 }} // Adjust position and zIndex
    >Start</button>} {/* Show button conditionally */}
    </>
  );
};

export default HoverEffectNodes;
