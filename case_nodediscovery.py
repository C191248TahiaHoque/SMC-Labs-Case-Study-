import asyncio
import json
from libp2p import (
    Peer,
    Swarm,
    listen_on,
    connect_to_peer,
    bootstrap,
    Protocol,
)
from libp2p.p2p.discover.discovery import Discovery

# Constants
PORT = 12345
DISCOVERY_INTERVAL = 10  # in seconds
TASK_TYPE_A = "type_a"
TASK_TYPE_B = "type_b"
TASK_TYPE_C = "type_c"

class PeerNode:
    def __init__(self, peer_id):
        self.peer_id = peer_id
        self.swarm = None
        self.discovery = None
        self.task_queue = {TASK_TYPE_A: [], TASK_TYPE_B: [], TASK_TYPE_C: []}

    async def start(self):
        """Start the node and listen for incoming connections."""
        self.swarm = await Swarm.create(listen_on(f'/ip4/0.0.0.0/tcp/{PORT}'))
        self.discovery = Discovery(self.swarm)
        await self.swarm.listen()
        print(f"Node {self.peer_id} started. Listening on {PORT}.")
        # Bootstrap: discover other peers
        await self.discovery.bootstrap()

        # Start periodic discovery (to keep up-to-date with peers)
        asyncio.create_task(self.periodic_discovery())

    async def periodic_discovery(self):
        """ Periodically discover peers to add new nodes. """
        while True:
            print(f"{self.peer_id} Discovering peers...")
            await self.discovery.discovery()
            await asyncio.sleep(DISCOVERY_INTERVAL)

    async def send_task_to_peer(self, peer_id, task_type, task_data):
        """Send a task to a peer."""
        peer_address = f"/ip4/127.0.0.1/tcp/{PORT}/p2p/{peer_id}"
        peer = Peer(peer_id)
        await connect_to_peer(peer, peer_address)
        message = {
            "task_type": task_type,
            "task_data": task_data
        }
        print(f"{self.peer_id} Sending task to {peer_id}: {message}")
        # Send task over the P2P network
        await self.swarm.send(peer, json.dumps(message).encode())
    async def handle_task(self, message):
        """Handle task received from other peers."""
        task = json.loads(message.decode())
        task_type = task['task_type']
        task_data = task['task_data']
        print(f"Received task of type {task_type} with data {task_data} on {self.peer_id}")      
        # Execute task based on its type
        result = f"Executed {task_type} task with data: {task_data}"
        return result
# Start peer node
async def main(peer_id):
    peer_node = PeerNode(peer_id)
    await peer_node.start()
    # For this example, we manually send a task to another peer
    if peer_id == "peer1":
        await peer_node.send_task_to_peer("peer2", TASK_TYPE_A, "Data for task A")  
    if peer_id == "peer2":
        # Example of receiving task on peer2
        result = await peer_node.handle_task('{"task_type": "type_a", "task_data": "Data for task A"}')
        print(f"Result of task: {result}")
if __name__ == "__main__":
    peer_id = "peer1"  # or "peer2" depending on which peer you run
    asyncio.run(main(peer_id))
