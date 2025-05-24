# Secure File Transfer Application

A modern web-based secure file transfer application with cryptographic signatures and real-time status tracking.

## Features

- **Secure File Transfer**: RSA-2048 digital signatures for file authenticity
- **Modern Web Interface**: Bootstrap-based responsive design with drag-and-drop upload
- **Real-time Status**: Live transfer progress tracking
- **Cryptographic Security**: SHA-256 hashing and PSS padding for integrity protection
- **File Validation**: Type and size restrictions for security
- **Professional UI**: Clean, intuitive interface with dark mode support

## Installation

1. Install Python 3.11 or higher
2. Install dependencies:
   ```bash
   pip install flask flask-sqlalchemy gunicorn cryptography email-validator psycopg2-binary werkzeug
   ```

3. Run the application:
   ```bash
   python main.py
   ```
   Or using Gunicorn:
   ```bash
   gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
   ```

## Usage

### Web Interface (Recommended)
1. Open your browser and go to `http://localhost:5000`
2. Use the **Send File** section to upload and send files
3. Use the **Receive File** section to listen for incoming files
4. Monitor transfer status in real-time

### Command Line Interface
- **Send a file**: `python client.py [file_path] [host] [port]`
- **Receive a file**: `python server.py [save_path] [host] [port]`

## File Structure

```
RSA/
├── app.py              # Main Flask application
├── main.py             # Application entry point
├── client.py           # File sending functionality
├── server.py           # File receiving functionality
├── crypto_utils.py     # Cryptographic operations
├── templates/          # HTML templates
│   ├── base.html
│   └── index.html
├── static/            # CSS, JS, and assets
│   ├── css/style.css
│   └── js/main.js
├── uploads/           # Temporary file storage
├── private_key.pem    # RSA private key (auto-generated)
└── public_key.pem     # RSA public key (auto-generated)
```

## Security Features

- **Digital Signatures**: Files are signed with RSA-2048 for authenticity verification
- **Integrity Protection**: SHA-256 hashing ensures files haven't been tampered with
- **Direct Transfer**: Peer-to-peer transfer without intermediate servers
- **File Type Validation**: Only allowed file types can be transferred
- **Size Limits**: Maximum file size of 16MB for security

## Configuration

- **Allowed File Types**: txt, pdf, png, jpg, jpeg, gif, doc, docx, zip, tar, gz
- **Maximum File Size**: 16MB
- **Default Port**: 12345
- **Key Size**: RSA-2048

## Requirements

- Python 3.11+
- Flask
- Cryptography library
- Bootstrap 5.3 (CDN)
- Font Awesome (CDN)

## License

This project is open source and available under the MIT License.