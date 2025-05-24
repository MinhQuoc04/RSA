import socket
import os
from crypto_utils import verify_signature

def server_receive(save_path, host='localhost', port=12345):
    """
    Receive a file with signature verification from a client
    """
    s = None
    conn = None
    
    try:
        # Create socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(60)  # 60 second timeout for connections
        
        # Bind and listen
        s.bind((host, port))
        s.listen(1)
        print(f"Server listening on {host}:{port}")
        
        # Accept connection
        conn, addr = s.accept()
        print(f"Connection accepted from {addr}")
        
        # Set timeout for data reception
        conn.settimeout(30)
        
        # Receive file size (4 bytes)
        file_size_bytes = conn.recv(4)
        if len(file_size_bytes) != 4:
            raise Exception("Failed to receive file size")
        
        file_size = int.from_bytes(file_size_bytes, 'big')
        print(f"Expecting file of size: {file_size} bytes")
        
        # Receive file data
        data = b''
        bytes_received = 0
        while bytes_received < file_size:
            chunk = conn.recv(min(4096, file_size - bytes_received))
            if not chunk:
                raise Exception("Connection lost while receiving file data")
            data += chunk
            bytes_received += len(chunk)
        
        print(f"Received file data: {len(data)} bytes")
        
        # Receive signature size (4 bytes)
        sig_size_bytes = conn.recv(4)
        if len(sig_size_bytes) != 4:
            raise Exception("Failed to receive signature size")
        
        sig_size = int.from_bytes(sig_size_bytes, 'big')
        print(f"Expecting signature of size: {sig_size} bytes")
        
        # Receive signature
        signature = b''
        bytes_received = 0
        while bytes_received < sig_size:
            chunk = conn.recv(min(4096, sig_size - bytes_received))
            if not chunk:
                raise Exception("Connection lost while receiving signature")
            signature += chunk
            bytes_received += len(chunk)
        
        print(f"Received signature: {len(signature)} bytes")
        
        # Create directory if it doesn't exist
        save_dir = os.path.dirname(save_path)
        if save_dir and not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)
        
        # Save file
        with open(save_path, 'wb') as f:
            f.write(data)
        
        # Verify signature
        if not os.path.exists("public_key.pem"):
            raise Exception("Public key not found. Cannot verify signature.")
        
        is_valid = verify_signature("public_key.pem", data, signature)
        
        if is_valid:
            print(f"✓ Signature verification PASSED")
            print(f"✓ File saved successfully to: {save_path}")
        else:
            print(f"✗ Signature verification FAILED")
            # Still save the file but warn the user
            print(f"⚠ File saved to: {save_path} (but signature is invalid)")
            raise Exception("Signature verification failed. File may be corrupted or tampered with.")
        
    except socket.timeout:
        raise Exception("Timeout waiting for connection or data")
    except OSError as e:
        if "Address already in use" in str(e):
            raise Exception(f"Port {port} is already in use. Try a different port.")
        else:
            raise Exception(f"Network error: {str(e)}")
    except Exception as e:
        # Clean up partial file on error
        if save_path and os.path.exists(save_path):
            try:
                os.remove(save_path)
                print(f"Cleaned up partial file: {save_path}")
            except:
                pass
        raise e
    finally:
        # Clean up connections
        if conn:
            try:
                conn.close()
            except:
                pass
        if s:
            try:
                s.close()
            except:
                pass

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        save_path = sys.argv[1]
        host = sys.argv[2] if len(sys.argv) > 2 else 'localhost'
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 12345
        server_receive(save_path, host, port)
    else:
        path = input("Enter path to save received file: ")
        host = input("Enter host to listen on (default: localhost): ").strip() or 'localhost'
        port = input("Enter port to listen on (default: 12345): ").strip()
        port = int(port) if port else 12345
        server_receive(path, host, port)
