import socket
import time
from crypto_utils import sign_data

def client_send(file_path, host='localhost', port=12345):
    """
    Send a file with cryptographic signature to a server
    """
    try:
        # Read file data
        with open(file_path, 'rb') as f:
            data = f.read()
        
        # Sign the data
        signature = sign_data("private_key.pem", data)
        
        # Create socket and connect
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(30)  # 30 second timeout
        
        try:
            s.connect((host, port))
            
            # Send file size first (4 bytes, big endian)
            file_size = len(data)
            s.sendall(file_size.to_bytes(4, 'big'))
            
            # Send file data
            s.sendall(data)
            
            # Send signature size (4 bytes, big endian)
            sig_size = len(signature)
            s.sendall(sig_size.to_bytes(4, 'big'))
            
            # Send signature
            s.sendall(signature)
            
            print(f"File sent successfully to {host}:{port}")
            print(f"File size: {file_size} bytes")
            print(f"Signature size: {sig_size} bytes")
            
        finally:
            s.close()
            
    except FileNotFoundError:
        raise Exception(f"File not found: {file_path}")
    except ConnectionRefusedError:
        raise Exception(f"Connection refused to {host}:{port}. Make sure the receiver is listening.")
    except socket.timeout:
        raise Exception("Connection timeout. The receiver may not be available.")
    except Exception as e:
        raise Exception(f"Failed to send file: {str(e)}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        host = sys.argv[2] if len(sys.argv) > 2 else 'localhost'
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 12345
        client_send(file_path, host, port)
    else:
        path = input("Enter file to send: ")
        host = input("Enter host (default: localhost): ").strip() or 'localhost'
        port = input("Enter port (default: 12345): ").strip()
        port = int(port) if port else 12345
        client_send(path, host, port)
