from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
import os

def generate_keys():
    """
    Generate RSA public/private key pair for signing and verification
    """
    try:
        print("Generating RSA key pair...")
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Get public key
        public_key = private_key.public_key()
        
        # Save private key
        with open("private_key.pem", "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Save public key
        with open("public_key.pem", "wb") as f:
            f.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
        
        print("✓ RSA key pair generated successfully")
        print("✓ Private key saved to: private_key.pem")
        print("✓ Public key saved to: public_key.pem")
        
    except Exception as e:
        raise Exception(f"Failed to generate keys: {str(e)}")

def sign_data(private_key_path, data):
    """
    Sign data using RSA private key with PSS padding and SHA-256
    """
    try:
        # Load private key
        with open(private_key_path, "rb") as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )
        
        # Sign the data
        signature = private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return signature
        
    except FileNotFoundError:
        raise Exception(f"Private key file not found: {private_key_path}")
    except Exception as e:
        raise Exception(f"Failed to sign data: {str(e)}")

def verify_signature(public_key_path, data, signature):
    """
    Verify signature using RSA public key with PSS padding and SHA-256
    """
    try:
        # Load public key
        with open(public_key_path, "rb") as f:
            public_key = serialization.load_pem_public_key(
                f.read(),
                backend=default_backend()
            )
        
        # Verify signature
        public_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return True
        
    except FileNotFoundError:
        raise Exception(f"Public key file not found: {public_key_path}")
    except Exception as e:
        print(f"Signature verification failed: {str(e)}")
        return False

def get_key_info():
    """
    Get information about existing keys
    """
    info = {
        'private_key_exists': os.path.exists('private_key.pem'),
        'public_key_exists': os.path.exists('public_key.pem'),
        'private_key_size': None,
        'public_key_size': None
    }
    
    if info['private_key_exists']:
        info['private_key_size'] = os.path.getsize('private_key.pem')
    
    if info['public_key_exists']:
        info['public_key_size'] = os.path.getsize('public_key.pem')
    
    return info

if __name__ == '__main__':
    # Interactive key management
    print("=== Cryptographic Key Management ===")
    
    info = get_key_info()
    
    if info['private_key_exists'] and info['public_key_exists']:
        print("✓ Key pair already exists")
        print(f"  Private key: {info['private_key_size']} bytes")
        print(f"  Public key: {info['public_key_size']} bytes")
        
        choice = input("\nGenerate new keys? (y/N): ").strip().lower()
        if choice == 'y':
            generate_keys()
    else:
        print("Key pair not found. Generating new keys...")
        generate_keys()
