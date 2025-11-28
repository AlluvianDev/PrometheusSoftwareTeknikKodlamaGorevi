import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import time

class NavigationMockNode(Node):
    def __init__(self):
        super().__init__('navigation_mock_node')

        # Subscribing to the target position coming from the coordinator
        self.nav_subscription = self.create_subscription(String,'navigation_goal',self.goal_callback,10)

        # Publisher reports the task result back to the coordinator
        self.status_publisher = self.create_publisher(String,'navigation_result',10)

        self.get_logger().info('Navigation Mock Node started')

    def goal_callback(self, msg):
        # Triggered when receiving a message containing (ID, POS) from the coordinator.
        # Example format: "ID:42; POS:1.0,2.0,0.0"
        
        data = msg.data.split(';')
        
        try:
            task_id = data[0].split(':')[1].strip()
            pos = data[1].split(':')[1].strip()
        except IndexError:
            self.get_logger().error(f"Error in target format: {msg.data}")
            return
            
        self.get_logger().info(f"Navigation Starting: Task ID {task_id}, Target {pos}")
        
        # Simulate moving to the target position
        self.simulate_movement(task_id, pos)

    def simulate_movement(self, task_id, pos):
        # Simulation of the movement (print and delay)
        
        # Wait 3 seconds for movement simulation
        self.get_logger().info(f"Simulation: Moving to {pos}...")
        time.sleep(3) # This is BLOCKING, but acceptable for a simple mock.
        
        # Assume simulation finished successfully
        success = True
        
        # Update the status and report back
        self.publish_result(task_id, success)

    def publish_result(self, task_id, success):
        
        # Report the completion or failure status back to the Coordinator
        # Sets status to "COMPLETED" if success is True, otherwise "FAILED"
        if success:
            status = "COMPLETED"
        else:
            status = "FAILED"
        
        result_msg = String()
        result_msg.data = f"RESULT;ID:{task_id};STATUS:{status}"
        
        self.status_publisher.publish(result_msg)
        self.get_logger().info(f"Navigation result published: {status}")

def main(args=None):
    rclpy.init(args=args)
    node = NavigationMockNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

    