class Task:


    def __init__(self,task_id,target_position,priority,task_type,timeout):
        self.task_id = task_id
        self.target_position = target_position
        self.priority = priority
        self.task_type = task_type
        self.timeout = timeout
        self.status = 'PENDING'
        
    #toString()
    def __repr__(self):
        return f"Task(ID: {self.task_id}, PRIO: {self.priority},TYPE: {self.task_type})"