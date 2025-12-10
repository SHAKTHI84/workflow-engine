import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    print("Testing API...")
    
    # 1. Health check
    try:
        r = requests.get(f"{BASE_URL}/")
        print(f"Health Check: {r.status_code} - {r.json()}")
    except Exception as e:
        print(f"Failed to connect: {e}")
        sys.exit(1)

    # 2. List tools
    r = requests.get(f"{BASE_URL}/tools")
    print(f"Tools: {r.json()}")

    # 3. Create a Custom Graph (Simple linear)
    # Graph: extract_functions -> check_complexity
    payload = {
        "nodes": [
            {"name": "step1", "tool": "extract_functions", "is_start": True},
            {"name": "step2", "tool": "check_complexity"}
        ],
        "edges": [
            {"from_node": "step1", "to_node": "step2"}
        ]
    }
    r = requests.post(f"{BASE_URL}/graph/create", json=payload)
    print(f"Create Graph: {r.status_code} - {r.json()}")
    if r.status_code != 200:
        sys.exit(1)
    
    graph_id = r.json()["graph_id"]

    # 4. Run the Custom Graph
    run_payload = {
        "graph_id": graph_id,
        "initial_state": {"code": "def hello():\n    print('world')\n\ndef world():\n    pass"}
    }
    r = requests.post(f"{BASE_URL}/graph/run", json=run_payload)
    print(f"Run Graph: {r.status_code} - {r.json()}")
    
    # 5. Run the Sample Code Review Graph
    sample_payload = {
        "graph_id": "sample-code-review",
        "initial_state": {
            "code": "import *\ndef bad():\n    print('bad')\n",
            "target_quality": 80,
            "max_retries": 2
        }
    }
    r = requests.post(f"{BASE_URL}/graph/run", json=sample_payload)
    print(f"Run Sample Graph: {r.status_code}")
    print("Sample Graph Log:", r.json().get("execution_log"))
    print("Sample Graph Final State:", r.json().get("final_state"))

if __name__ == "__main__":
    test_api()
