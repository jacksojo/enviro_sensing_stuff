# webrepl_setup.py
import webrepl
import network

def setup_webrepl(wifi_ssid, wifi_password, webrepl_password):
    """
    Helper function to set up WebREPL
    
    Args:
        wifi_ssid (str): WiFi network name
        wifi_password (str): WiFi password
        webrepl_password (str): Password for WebREPL access
    """
    # Connect to WiFi
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(wifi_ssid, wifi_password)
    
    # Wait for connection
    while not wlan.isconnected():
        print('Waiting for WiFi connection...')
        time.sleep(1)
    
    # Print network details
    print('Network Config:', wlan.ifconfig())
    
    # Start WebREPL
    webrepl.start(password=webrepl_password)
    print('WebREPL started. Connect using WebREPL client.')

# Example usage
if __name__ == '__main__':
    setup_webrepl('ssid', 'wifi_password', 'repl_password')