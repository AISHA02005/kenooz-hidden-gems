def test_health_check(client):
    """Test that the /api/health endpoint returns 200 and healthy status."""
    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "kenooz-api"
    assert "version" in data
