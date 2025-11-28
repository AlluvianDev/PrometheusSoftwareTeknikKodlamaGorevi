import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import time

# Project Imports
from .Task import Task 
from .TaskQueue import TaskQueue # Import the TaskQueue class
from .QRParse import QRParse 

class TaskCoordinatorNode(Node):
    
    # Task Coordinator ROS 2 Node for Prometheus Rover.
    # Manages logistic tasks, processes QR codes, integrates with navigation, and reports status.
    
    def __init__(self):
        super().__init__('task_coordinator_node')
        
        # TASK QUEUE MANAGEMENT (Using the external TaskQueue class)
        self.task_manager = TaskQueue() # Initialize TaskQueue instance
        
        # ROS COMMUNICATION CHANNELS
        
        # 1. Subscriber to listen for QR Codes (TASK ADDITION)
        self.qr_subscription = self.create_subscription(
            String,
            'qr_code_data',
            self.qr_callback, 
            10)
            
        # 2. Publisher to send commands to Navigation (TASK START)
        self.nav_publisher = self.create_publisher(String, 'navigation_goal', 10)

        # 3. Publisher for Status Reporting (MQTT Mock - PDF Requirement 4)
        self.status_publisher = self.create_publisher(String, 'task_status', 10)
        
        # 4. Subscriber for Navigation Feedback (TASK COMPLETION/FAILURE)
        self.result_subscription = self.create_subscription(
            String,
            'navigation_result', 
            self.navigation_result_callback,
            10)

        # 5. TIMER to Periodically Run Task Management (Replaces blocking while loops)
        timer_period = 1.0  # Check the queue every 1 second
        self.timer = self.create_timer(timer_period, self.manage_task_queue)
        
        self.get_logger().info('Task Coordinator Node Started (Jazzy).')
        
    # --- HELPER METHODS ---

    def report_status(self, task):
        # Sends task status to the MQTT topic (simulated with print/log).
        
        status_msg = String()
        # Report ID, Type, and NEW_STATUS information.
        status_msg.data = f"TASK_UPDATE;ID:{task.task_id};TYPE:{task.task_type};NEW_STATUS:{task.status}"
        self.status_publisher.publish(status_msg)
        self.get_logger().info(f"MQTT Report Simulation: {status_msg.data}")

    def send_navigation_goal(self, task):
        # Sends target coordinates to the Navigation Mock.
        goal_msg = String()
        pos_str = ",".join(map(str, task.target_position)) 
        goal_msg.data = f"ID:{task.task_id};POS:{pos_str}"
        self.nav_publisher.publish(goal_msg)
        self.get_logger().info(f"Navigation goal sent: {pos_str}")

    # --- CALLBACK METHODS (Triggered by Topics) ---

    def qr_callback(self, msg):
        
        # Parses the string coming from the 'qr_code_data' topic and adds it to the queue.
        
        qr_string = msg.data
        # Call the parse_qr_string function from the QRParse module
        parsed_task = QRParse.parse_qr_string(qr_string) 
        
        if parsed_task:
            self.task_manager.add_task(parsed_task) # Add task via TaskQueue class
            self.get_logger().info(f"QR code successfully processed and task {parsed_task.task_id} added to queue. Queue size: {len(self.task_manager.tasks)}")
        else:
            self.get_logger().warn(f"Invalid QR format detected. Task not added.")

    def navigation_result_callback(self, msg):
        
        # Processes the task completion/failure message from the Navigation Mock.
        
        data_parts = msg.data.split(';')
        
        try:
            task_id = data_parts[1].split(':')[1].strip()
            status = data_parts[2].split(':')[1].strip() # COMPLETED or FAILED
        except IndexError:
            self.get_logger().error(f"Invalid navigation result format: {msg.data}")
            return

        # Check if the result belongs to the currently running task
        if self.task_manager.current_task is None or str(self.task_manager.current_task.task_id) != task_id:
            self.get_logger().warn(f"Unexpected result: ID {task_id} is not currently active.")
            return

        # Pass the result to the TaskQueue manager to finalize the task status
        success = status == "COMPLETED"
        finished_task = self.task_manager.finish_current_task(success=success, reason=status)
        
        if finished_task:
            self.report_status(finished_task) # Report the final status

    # --- MANAGEMENT METHODS (Triggered by Timer) ---
    
    def manage_task_queue(self):
        
        # Main management function triggered periodically by the Timer.
        # Ensures that only one task can run at a time.
        
        next_task = self.task_manager.get_next_task() # Get next high-priority task from queue
        
        if next_task is None:
            # Queue is empty or a task is already running (checked inside get_next_task)
            return

        # New task retrieved, starting execution
        self.get_logger().info(f"NEW TASK STARTING: {next_task.task_id} ({next_task.task_type})")

        self.report_status(next_task) # Report IN_PROGRESS status

        task_type = next_task.task_type
        
        if task_type in ["pickup", "delivery", "scan"]:
            # Send the command to the Navigation Mock and wait for the result
            self.send_navigation_goal(next_task)
            
        elif task_type == "wait":
            # WAIT task: No navigation required, immediately complete (Simple simulation)
            timeout = next_task.timeout
            self.get_logger().info(f"WAIT task waiting for {timeout} seconds (Immediately completing simulation).")
            
            # Use TaskQueue to complete the task immediately
            finished_task = self.task_manager.finish_current_task(success=True) 
            self.report_status(finished_task) # Report COMPLETED status
            
        else:
            self.get_logger().warn(f"Unknown Task Type: {task_type}. Marking as failed.")
            finished_task = self.task_manager.finish_current_task(success=False)
            self.report_status(finished_task)

# Main ROS 2 Function
def main(args=None):
    rclpy.init(args=args)
    node = TaskCoordinatorNode()
    try:
        rclpy.spin(node) 
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()