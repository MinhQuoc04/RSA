import os
import threading
import time
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from client import client_send
from server import server_receive
from crypto_utils import generate_keys
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "secure_file_transfer_key_2024")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'zip', 'tar', 'gz'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Global variables for transfer status
transfer_status = {
    'active': False,
    'type': None,  # 'send' or 'receive'
    'progress': 0,
    'message': 'Ready',
    'filename': None,
    'error': None
}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Generate keys if they don't exist
if not os.path.exists("private_key.pem"):
    generate_keys()

@app.route('/')
def index():
    # Check if keys exist
    keys_exist = os.path.exists("private_key.pem") and os.path.exists("public_key.pem")
    return render_template('index.html', 
                         keys_exist=keys_exist, 
                         transfer_status=transfer_status)

@app.route('/send', methods=['POST'])
def send_file():
    global transfer_status
    
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    if not allowed_file(file.filename):
        flash('File type not allowed', 'error')
        return redirect(url_for('index'))
    
    host = request.form.get('host', 'localhost').strip()
    try:
        port = int(request.form.get('port', 12345))
        if port < 1 or port > 65535:
            raise ValueError("Port out of range")
    except ValueError:
        flash('Invalid port number', 'error')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Start file transfer in background thread
        def send_file_thread():
            global transfer_status
            try:
                transfer_status.update({
                    'active': True,
                    'type': 'send',
                    'progress': 0,
                    'message': f'Sending {filename}...',
                    'filename': filename,
                    'error': None
                })
                
                transfer_status['progress'] = 25
                transfer_status['message'] = 'Connecting to server...'
                
                client_send(filepath, host, port)
                
                transfer_status.update({
                    'active': False,
                    'progress': 100,
                    'message': f'File {filename} sent successfully!',
                    'type': 'send'
                })
                
                # Clean up uploaded file after successful send
                if os.path.exists(filepath):
                    os.remove(filepath)
                    
            except Exception as e:
                transfer_status.update({
                    'active': False,
                    'progress': 0,
                    'message': f'Error sending file: {str(e)}',
                    'error': str(e),
                    'type': 'send'
                })
                logging.error(f"Error sending file: {e}")
        
        thread = threading.Thread(target=send_file_thread)
        thread.daemon = True
        thread.start()
        
        flash(f'Started sending {filename}', 'info')
    
    return redirect(url_for('index'))

@app.route('/receive', methods=['POST'])
def receive_file():
    global transfer_status
    
    save_path = request.form.get('save_path', '').strip()
    if not save_path:
        flash('Please specify a save path', 'error')
        return redirect(url_for('index'))
    
    host = request.form.get('receive_host', 'localhost').strip()
    try:
        port = int(request.form.get('receive_port', 12345))
        if port < 1 or port > 65535:
            raise ValueError("Port out of range")
    except ValueError:
        flash('Invalid port number', 'error')
        return redirect(url_for('index'))
    
    # Start file receive in background thread
    def receive_file_thread():
        global transfer_status
        try:
            transfer_status.update({
                'active': True,
                'type': 'receive',
                'progress': 0,
                'message': f'Waiting for file on {host}:{port}...',
                'filename': save_path,
                'error': None
            })
            
            transfer_status['progress'] = 25
            transfer_status['message'] = 'Server listening...'
            
            server_receive(save_path, host, port)
            
            transfer_status.update({
                'active': False,
                'progress': 100,
                'message': f'File received and saved to {save_path}',
                'type': 'receive'
            })
            
        except Exception as e:
            transfer_status.update({
                'active': False,
                'progress': 0,
                'message': f'Error receiving file: {str(e)}',
                'error': str(e),
                'type': 'receive'
            })
            logging.error(f"Error receiving file: {e}")
    
    thread = threading.Thread(target=receive_file_thread)
    thread.daemon = True
    thread.start()
    
    flash(f'Started listening for file on {host}:{port}', 'info')
    return redirect(url_for('index'))

@app.route('/status')
def get_status():
    """API endpoint to get current transfer status"""
    return jsonify(transfer_status)

@app.route('/generate_keys', methods=['POST'])
def regenerate_keys():
    """Generate new cryptographic keys"""
    try:
        generate_keys()
        flash('New cryptographic keys generated successfully', 'success')
    except Exception as e:
        flash(f'Error generating keys: {str(e)}', 'error')
        logging.error(f"Error generating keys: {e}")
    
    return redirect(url_for('index'))

@app.route('/clear_status', methods=['POST'])
def clear_status():
    """Clear the current transfer status"""
    global transfer_status
    transfer_status.update({
        'active': False,
        'type': None,
        'progress': 0,
        'message': 'Ready',
        'filename': None,
        'error': None
    })
    return redirect(url_for('index'))

@app.errorhandler(413)
def file_too_large(error):
    flash('File too large. Maximum size is 16MB.', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
