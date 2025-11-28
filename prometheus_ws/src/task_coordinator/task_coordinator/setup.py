entry_points={
        'console_scripts': [
            # These lines are telling ROS2 which command runs which file 
            'coordinator_node = task_coordinator.coordinator_node:main',
            'navigation_mock_node = task_coordinator.navigation_mock_node:main',
        ],
    },