import socketpool
import wifi


class Utils:

    def is_number(value):
        return isinstance(value, (float, int))
    
    def get_secrets():
        try:
            from secrets import secrets
        except ImportError:
            print("Failed to import secrets.py")
            raise
        
        return secrets

    def connect_to_wifi(ssid, password):
        try:
            print(f'Connecting to {ssid}')
            wifi.radio.connect(ssid, password)
            print(f'Connected to {ssid}; IPv4 address = {wifi.radio.ipv4_address}')
        except:
            print("Error connecting to WiFi")
            raise

    def get_socket(interface, port):
        pool = socketpool.SocketPool(wifi.radio)
        
        socket = pool.socket()
        socket.bind([interface, port])
        socket.settimeout(1)
        socket.listen(1)

        return socket