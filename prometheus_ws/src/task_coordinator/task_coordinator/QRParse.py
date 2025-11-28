from .Task import Task

class QRParse:
    @staticmethod
    def parse_qr_string(qr_string: str) -> Task:
        #Returns none if the object is not str
        if not qr_string:
            print("QR code string is empty")
            return None
        

        fields = qr_string.split(";")
        task_data = {}

        for field in fields:

            try:
                parts = field.split(":",1) #split from : and return 1 value

                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    task_data[key] = value
                    print(f"{key} -> {value}")
                else:
                    #Pass was recommended for ros node log
                    pass
                
            except Exception as e:
                print(f"Exception {e} occurred during parse_qr_string split")
                return None

        try:
                task_id = int(task_data["ID"])
                pos = task_data["POS"]
                prio = int(task_data["PRIO"])
                task_type = task_data["TYPE"]
                timeout = int(task_data["TIMEOUT"])
                # Turning values to their necessarry types in Task
                task_id = int(task_id)

                target_position = []
                for coordinate in pos.split(","):
                    target_position.append(float(coordinate))
                #Checking for correct priority values
                if not 1 <= prio <= 5:
                    print(f"Error: {prio} priority is not between (1-5)")
                    return None
                valid_task_types = {"pickup", "delivery", "scan", "wait"}

                #Checking for correct task type values
                if task_type not in valid_task_types:
                    print(f"Error: {task_type} not a valid task type")
                    return None
                
                print(f"ID:{task_id};POS:{target_position};PRIO:{prio};TYPE:{type};TIMEOUT:{timeout}")
                return Task(task_id, target_position, prio, task_type, timeout)
                
        except KeyError as e:
                print(f"Field is missing: {e}.")
                return None
        except ValueError as e:
                print(f"Invalid value for {e}.")
                return None
        

