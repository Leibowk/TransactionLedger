"""API tests: HTTP endpoints with test DB (get_db overridden)."""
import pytest
from fastapi.testclient import TestClient


def test_get_account_ok(client: TestClient, test_account):
    """GET /accounts/{id} returns 200 and account when account exists."""
    response = client.get(f"/accounts/{test_account.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_account.id
    assert data["name"] == test_account.name
    assert data["masked_account_number"] == test_account.masked_account_number
    assert "available_balance" in data
    assert "current_balance" in data
    assert "member" in data
    assert data["member"]["first_name"] == "Test"


def test_get_account_not_found(client: TestClient):
    """GET /accounts/{id} returns 404 when account does not exist."""
    response = client.get("/accounts/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Account not found"


def test_get_transactions_ok(client: TestClient, test_account):
    """GET /accounts/{id}/transactions returns 200 and list (may be empty)."""
    response = client.get(f"/accounts/{test_account.id}/transactions")
    assert response.status_code == 200
    assert response.json() == []


def test_get_transactions_account_not_found(client: TestClient):
    """GET /accounts/{id}/transactions returns 404 when account does not exist."""
    response = client.get("/accounts/999999/transactions")
    assert response.status_code == 404
    assert response.json()["detail"] == "Account not found"


def test_post_transaction_credit_ok(client: TestClient, test_account):
    """POST /accounts/{id}/transactions with CREDIT returns 200 and transaction."""
    response = client.post(
        f"/accounts/{test_account.id}/transactions",
        json={
            "amount": "50.00",
            "counterparty": "Employer",
            "type": "CREDIT",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] in (50.0, "50.00", 50)
    assert data["counterparty"] == "Employer"
    assert data["type"] == "CREDIT"
    assert data["status"] == "PENDING"
    assert "id" in data
    assert "timestamp" in data


def test_post_transaction_debit_ok(client: TestClient, test_account):
    """POST /accounts/{id}/transactions with DEBIT (within balance) returns 200."""
    response = client.post(
        f"/accounts/{test_account.id}/transactions",
        json={
            "amount": "25.00",
            "counterparty": "Store",
            "type": "DEBIT",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "DEBIT"
    assert data["status"] == "PENDING"


def test_post_transaction_insufficient_funds(client: TestClient, test_account):
    """POST /accounts/{id}/transactions DEBIT over balance returns 400."""
    response = client.post(
        f"/accounts/{test_account.id}/transactions",
        json={
            "amount": "200.00",
            "counterparty": "Store",
            "type": "DEBIT",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient funds"


def test_post_transaction_account_not_found(client: TestClient):
    """POST /accounts/{id}/transactions returns 404 when account does not exist."""
    response = client.post(
        "/accounts/999999/transactions",
        json={"amount": "10.00", "counterparty": "X", "type": "CREDIT"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Account not found"


def test_post_transaction_validation_error(client: TestClient, test_account):
    """POST with invalid body returns 422."""
    response = client.post(
        f"/accounts/{test_account.id}/transactions",
        json={"amount": "10.00", "type": "CREDIT"},
    )
    assert response.status_code == 422


def test_patch_transaction_settle_ok(client: TestClient, test_account):
    """PATCH to SETTLED on a PENDING transaction returns 200."""
    create_resp = client.post(
        f"/accounts/{test_account.id}/transactions",
        json={"amount": "10.00", "counterparty": "X", "type": "CREDIT"},
    )
    assert create_resp.status_code == 200
    tx_id = create_resp.json()["id"]

    response = client.patch(
        f"/accounts/{test_account.id}/transactions/{tx_id}",
        json={"status": "SETTLED"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "SETTLED"


def test_patch_transaction_fail_ok(client: TestClient, test_account):
    """PATCH to FAILED on a PENDING transaction returns 200."""
    create_resp = client.post(
        f"/accounts/{test_account.id}/transactions",
        json={"amount": "10.00", "counterparty": "X", "type": "CREDIT"},
    )
    assert create_resp.status_code == 200
    tx_id = create_resp.json()["id"]

    response = client.patch(
        f"/accounts/{test_account.id}/transactions/{tx_id}",
        json={"status": "FAILED"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "FAILED"


def test_patch_transaction_not_found(client: TestClient, test_account):
    """PATCH when transaction does not exist returns 404."""
    response = client.patch(
        f"/accounts/{test_account.id}/transactions/999999",
        json={"status": "SETTLED"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Transaction not found"


def test_patch_transaction_invalid_transition(client: TestClient, test_account):
    """PATCH to SETTLED on already SETTLED transaction returns 400."""
    create_resp = client.post(
        f"/accounts/{test_account.id}/transactions",
        json={"amount": "10.00", "counterparty": "X", "type": "CREDIT"},
    )
    assert create_resp.status_code == 200
    tx_id = create_resp.json()["id"]
    client.patch(
        f"/accounts/{test_account.id}/transactions/{tx_id}",
        json={"status": "SETTLED"},
    )

    response = client.patch(
        f"/accounts/{test_account.id}/transactions/{tx_id}",
        json={"status": "SETTLED"},
    )
    assert response.status_code == 400
    assert "not pending" in response.json()["detail"].lower() or "transition" in response.json()["detail"].lower()
