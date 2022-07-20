# define the range for the first message UID
message_uid_start_min = 0
message_uid_start_max = 1_000_000

# define the robot templates
robot_templates = [{'name': 'Arnie',  'model': 'T-800',  'description': 'GOOD'},
                   {'name': 'Robert', 'model': 'T-1000', 'description': 'BAD'},
                   ]

# define the initial position
robot_init_position = (0, 0)

# define server parameters: url, port, and max workers
server_url = '[::]'
server_port = 9000
server_max_workers = 5
