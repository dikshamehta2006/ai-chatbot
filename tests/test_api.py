from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.database import init_db

init_db()

def run_tests():
    with TestClient(app) as client:
        # 1. Root
        res = client.get("/")
        assert res.status_code == 200
        assert "Multimodal Emotional Support Chatbot" in res.json()["message"]
        print("✓ Root endpoint passed")

        # 2. Health
        res = client.get("/api/v1/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert "database" in data
        assert "rag" in data
        print("✓ Health endpoint passed")

        # 3. Session creation
        res = client.post("/api/v1/session/new")
        assert res.status_code == 200
        session_id = res.json()["session_id"]
        assert session_id.startswith("sess_")
        print("✓ Session creation passed")

        # 4. Chat Crisis Flow
        crisis_data = {
            "session_id": session_id,
            "message": "I can't take this anymore, I want to kill myself",
            "generate_audio": False
        }
        res = client.post("/api/v1/chat/message", data=crisis_data)
        assert res.status_code == 200
        res_json = res.json()
        assert res_json["is_crisis"] is True
        assert "988" in res_json["response"] or "Lifeline" in res_json["response"]
        print("✓ Crisis flow guardrail passed")

        # 5. Chat Safe Message
        safe_data = {
            "session_id": session_id,
            "message": "Can you guide me through a 5-4-3-2-1 sensory grounding exercise?",
            "generate_audio": False
        }
        res = client.post("/api/v1/chat/message", data=safe_data)
        assert res.status_code == 200
        res_json = res.json()
        assert res_json["is_crisis"] is False
        assert len(res_json["response"]) > 20
        print("✓ Safe chat message passed")

if __name__ == "__main__":
    run_tests()
    print("All API Tests Passed Successfully!")
