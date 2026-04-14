import logging
import os
import webbrowser
import threading
import time
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from core.logic import (
    build_parity_check_matrix, 
    analyze_single_graph, 
    to_serializable
)

# Initialize Flask app
app = Flask(__name__, static_folder='static')
CORS(app)

# Avoid noisy werkzeug logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/')
def index():
    """Serve the main UI page."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static assets (JS, CSS, images)."""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/compute', methods=['POST'])
def compute():
    """
    Compute parity check matrix, logical operators, and distance 
    based on the graph provided by the UI.
    """
    data = request.json
    cluster_dict = data.get("cluster_connections", {})
    message_dict = data.get("message_connections", {})
    d_str = data.get("d", None)
    
    if not cluster_dict:
        return jsonify({"error": "No cluster nodes provided."}), 400

    try:
        # Build the initial matrices from adjacency data
        A_cc, A_cm, H, info = build_parity_check_matrix(cluster_dict, message_dict)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    n = info["n"]
    k = info["k"]

    response_payload = {
        "A_cc_shape": list(A_cc.shape),
        "A_cc": A_cc.tolist(),
        "A_cm_shape": list(A_cm.shape),
        "A_cm": A_cm.tolist(),
        "H_shape": list(H.shape),
        "H": H.tolist(),
        "n": n,
        "k": k,
        "results": [],
        "single_result": None,
        "parity_check_matrix": None
    }

    if k == 0:
        response_payload["message"] = "Add at least one message node to compute logical operators and distance."
    else:
        try:
            # Perform exact distance analysis and logical operator extraction
            full_result, parity_check_m = analyze_single_graph(A_cc, A_cm, n, k)
            response_payload["parity_check_matrix"] = parity_check_m.tolist()
            response_payload["single_result"] = to_serializable(full_result)
        except Exception as exc:
            return jsonify({"error": str(exc)}), 400

    return jsonify(response_payload)

def open_browser():
    """Wait for server to start, then open browser."""
    # Small delay to ensure server is up
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == '__main__':
    print("--------------------------------------------------")
    print("Quantum Cluster Parity Check App")
    print("Starting local server at http://127.0.0.1:5000")
    print("The UI should open automatically in your browser.")
    print("--------------------------------------------------")
    
    # Start browser in a separate thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run the server
    app.run(port=5000, debug=False)
