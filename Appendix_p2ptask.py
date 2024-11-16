import threading

# Constants
PORT = 12345
TASK_ORDER = ["a1", "a2", "c1", "b1", "c2", "a3", "b2", "b3", "a4", "c3", "b4"]
TASK_TYPES = {'a': [], 'b': [], 'c': []}

class PeerNode:
    def __init__(self, peer_id, task_type, order, swarm):
        self.peer_id = peer_id
        self.task_type = task_type
        self.order = order
        self.swarm = swarm
        self.task_lock = threading.Lock()

    async def start(self):
        """Start the node and listen for incoming connections."""
        print("Node {self.peer_id} started, waiting for tasks of type {self.task_type}.")

    async def send_task_to_peer(self, peer_id, task):
        """Send a task to a peer."""
        peer_address = f"/ip4/127.0.0.1/tcp/{PORT}/p2p/{peer_id}"
        peer = Peer(peer_id)
        await connect_to_peer(peer, peer_address)

        message = json.dumps({"task_type": task[0], "task_id": task[1]})
        print(f"{self.peer_id} sending task: {message}")
        # Send task over the P2P network
        await self.swarm.send(peer, message.encode())

    def execute_task(self, task):
        """Execute the task after acquiring the lock."""
        with self.task_lock:
            print(f"{self.peer_id} executing task: {task[0]}{task[1]}")
            return f"Executed {task[0]}{task[1]}"

    async def handle_task(self, task_message):
        """Handle received task message."""
        task = json.loads(task_message.decode())
        task_type = task['task_type']
        task_id = task['task_id']

        # Ensure the task matches the node's type
        if task_type == self.task_type:
            result = self.execute_task((task_type, task_id))
            print(f"Result of {task_type} task: {result}")
        else:
            print(f"Task {task_id} doesn't belong to this node type.")
            # If task type doesn't match, ignore or propagate it.

async def main():
    swarm = await Swarm.create(listen_on(f'/ip4/127.0.0.1/tcp/{PORT}'))
    # Initialize nodes for each task type (a, b, c)
    node_a = PeerNode('peer_a', 'a', TASK_ORDER, swarm)
    node_b = PeerNode('peer_b', 'b', TASK_ORDER, swarm)
    node_c = PeerNode('peer_c', 'c', TASK_ORDER, swarm)
    # Start all nodes
    await node_a.start()
    await node_b.start()
    await node_c.start()

    # Each node will handle tasks from its corresponding task type
    for task in TASK_ORDER:
        task_type = task[0]  # 'a', 'b', or 'c'
        task_id = task

        if task_type == 'a':
            await node_a.send_task_to_peer('peer_a', (task_type, task_id))
        elif task_type == 'b':
            await node_b.send_task_to_peer('peer_b', (task_type, task_id))
        elif task_type == 'c':
            await node_c.send_task_to_peer('peer_c', (task_type, task_id))

    # Wait for tasks to complete (this can be expanded to handle task completions)
    await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
