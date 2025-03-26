import time

class Logger:
    def __init__(self, log_file='sensor.log', max_lines=1000):
        self.log_file = log_file
        self.max_lines = max_lines
        
    def log(self, message, level='INFO'):
        timestamp = time.localtime()
        time_str = f"{timestamp[0]}-{timestamp[1]:02d}-{timestamp[2]:02d} {timestamp[3]:02d}:{timestamp[4]:02d}:{timestamp[5]:02d}"
        log_entry = f"{time_str} [{level}] {message}\n"
        
        try:
            # Also print to console for debugging
            print(log_entry.strip())
            
            with open(self.log_file, 'a') as f:
                f.write(log_entry)
            
            # Trim log file if too long
            self._trim_logs()
                
        except Exception as e:
            print(f"Logging failed: {e}")
            
    def _trim_logs(self):
        try:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
            if len(lines) > self.max_lines:
                with open(self.log_file, 'w') as f:
                    f.writelines(lines[-self.max_lines:])
        except:
            pass