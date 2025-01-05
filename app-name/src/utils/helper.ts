'server'
import { fetchAllFileItems, FileItem } from '../api/item';


export default async function fetchAndCreateNodes(nodes: Node[]) {
    try {
        const result: FileItem[] = await fetchAllFileItems();
        console.log(result);
        
        let newNode: any[] = []; // Initialize an array to hold new nodes

        console.log("YEs");
        if (result) {
            console.log("First Check");
            for (const item of result) {
                if (item.function_list) {
                    for (const functionItem of item.function_list) { // Iterate over function_list
                        const newNodeId = `func-${functionItem.token}`;
                        if (nodes.some(node => node.id === newNodeId)) {
                            console.log(`Node with id ${newNodeId} already exists, skipping...`);
                            continue;
                        }
                        console.log("Adding NODE");
                        newNode.push({ // Append new node info to newNode array
                            id: newNodeId,
                            type: 'default',
                            data: { label: functionItem.token }, // Use functionItem.token
                            position: { x: 100 + nodes.length * 100, y: 100 },
                            style: { 
                                backgroundColor: '#dbdbdb',
                                width: 150,
                                height: 50,
                                display: 'block'
                            }
                        });
                        console.log("THis is the type of functionITem process");
                        functionItem.process.forEach((item) => {
                            if (typeof item === 'string') {
                                console.log("String item:", item);
                                newNode.push({ // Append new node info to newNode array
                                    id: `func-${functionItem.token}-process-${item}`,
                                    type: 'default',
                                    data: { label: `${functionItem.token}-process-${item}`}, // Use functionItem.token
                                    position: { x: 100 + nodes.length * 100, y: 100 },
                                    style: { 
                                        backgroundColor: '#dbdbdb',
                                        width: 150,
                                        height: 50,
                                        display: 'block'
                                    }
                                });
                            } else if ('points_to' in item) { // Assuming isCall is a type guard for Call type
                                console.log("Variable item:", item);
                                newNode.push({ // Append new node info to newNode array
                                    id: `func-${functionItem.token}-Variable-${item.token}`,
                                    type: 'default',
                                    data: { label: `${functionItem.token}-Variable-${item.token}`}, // Use functionItem.token
                                    position: { x: 100 + nodes.length * 100, y: 100 },
                                    style: { 
                                        backgroundColor: '#dbdbdb',
                                        width: 150,
                                        height: 50,
                                        display: 'block'
                                    }
                                });
                            } else {
                                console.log("Calls item:", item);
                                newNode.push({ // Append new node info to newNode array
                                    id: `func-${functionItem.token}-Call-${item.func_token}`,
                                    type: 'default',
                                    data: { label: `${functionItem.token}-Call-${item.func_token}`}, // Use functionItem.token
                                    position: { x: 100 + nodes.length * 100, y: 100 },
                                    style: { 
                                        backgroundColor: '#dbdbdb',
                                        width: 150,
                                        height: 50,
                                        display: 'block'
                                    }
                                });
                                
                            }
                        });
                        

                        // if (process )
                            // const newNodeId = `func-${process.token}`;
                            // newNode.push({ // Append new node info to newNode array
                            //     id: newNodeId,
                            //     type: 'default',
                            //     data: { label: process.token }, // Use functionItem.token
                            //     position: { x: 100 + nodes.length * 100, y: 100 },
                            //     style: { 
                            //         backgroundColor: '#dbdbdb',
                            //         width: 150,
                            //         height: 50,
                            //         display: 'block'
                            //     }
                            // });

                    }
                }
            }
        }
        return newNode;

    } catch (error) {
        console.error("Error in fetchAndCreateNodes:", error);
    }
}

