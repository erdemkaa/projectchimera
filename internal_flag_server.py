from flask import Flask
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/secret_flag')
def secret_flag():
    logger.info("Internal flag server accessed at /secret_flag")
    return "flag{VAULT_TEC_INTERNAL_SURVEILLANCE_UNCOVERED}"

@app.route('/')
def index():
    return "Internal Vault-Tec Service: Access Denied."

if __name__ == '__main__':
    # This server should run on a port not exposed externally, e.g., 8080
    app.run(host='127.0.0.1', port=8080, debug=False)
