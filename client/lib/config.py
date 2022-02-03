conn_arg = {"user": "alan", 
                "password": "123",
                "host": "192.168.0.111",
                "port": 5672,
                "virtual_host": "solarity",
                "exchange": "topic_logs",
                "routing_key": "mm",
                "queue" : "market_message"} 

display_conn = {"user": "alan", 
                "password": "123",
                "host": "192.168.0.111",
                "port": 5672,
                "virtual_host": "solarity",
                "exchange": "exchange_message",
                "queue" : "market_queue"} 


ui_conn = {"user": "alan", 
        "password": "123",
        "host": "192.168.0.111",
        "port": 5672,
        "virtual_host": "solarity",
        "exchange": "exchange_message",
        "queue" : "pyqt6"} 