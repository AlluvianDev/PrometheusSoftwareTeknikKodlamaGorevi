from .Task import Task 
# Not using time in here, it holds the ros process

class TaskQueue:
    
    #Core Data Manager for Task Coordination. 
    #Handles task storage, sorting, and state management, completely decoupled from ROS communication.
    
    def __init__(self):
        # List of PENDING tasks
        self.tasks: list[Task] = [] 
        # The currently running task. Must be None to start a new task (Single-task execution rule).
        self.current_task: Task = None 

    def add_task(self, task: Task):
        #Adds a new task to the queue and sets its initial status (PENDING).
        task.status = 'PENDING' 
        self.tasks.append(task)
        # Using print() here is okay, but ROS Node logger is preferred for production.

    def sort_by_priority(self):
        #Sorts the queue based on task priority (1 being highest).
        self.tasks.sort(key=lambda task: task.priority)
        
    def get_next_task(self) -> Task | None:
        
        #Fetches the next highest-priority task if no task is currently running.
        #The caller (TaskCoordinatorNode) is responsible for executing this task.
        
        if self.current_task is not None:
            # CHECK: Only one task running at a time.
            return None
        
        if not self.tasks:
            # CHECK: Queue is empty.
            return None

        self.sort_by_priority()
        
        # Pop the highest priority task (first element).
        next_task = self.tasks.pop(0) 
        self.current_task = next_task
        
        # Set the state before starting execution.
        self.current_task.status = 'IN_PROGRESS' 
        return self.current_task

    def finish_current_task(self, success: bool, reason: str = ""):
        
        #Updates the status of the current task based on result (Navigation Mock). 
        #Resets 'current_task' to allow the next task to run.
        
        if self.current_task is None:
            return None

        # Determine the final status (COMPLETED, FAILED, or TIMEOUT).
        if success:
            self.current_task.status = 'COMPLETED'
        else:
            self.current_task.status = 'FAILED'
            if "TIMEOUT" in reason:
                self.current_task.status = 'TIMEOUT'
        
        # Store the completed/failed task reference for reporting.
        finished_task = self.current_task
        # CRITICAL: Free up the queue manager to accept the next task.
        self.current_task = None 
        
        return finished_task