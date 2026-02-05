"""API tests: HTTP endpoints with test DB (get_db overridden)."""
import pytest
from httpx import AsyncClient


async def test_get_account_ok(client: AsyncClient, test_account):
    """GET /accounts/{id} returns 200 and account when account exists."""
    response = await client.get(f"/accounts/{test_account.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_account.id
    assert data["name"] == test_account.name
    assert data["masked_account_number"] == test_account.masked_account_number
    assert "available_balance" in data
    assert "current_balance" in data
    assert "member" in data
    assert data["member"]["first_name"] == "Test"


async def test_get_member_accounts_ok(client: AsyncClient, test_account):
    """GET /members/{id}/accounts returns 200 and list of accounts."""
    member_id = test_account.member_id
    response = await client.get(f"/members/{member_id}/accounts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(a["id"] == test_account.id for a in data)


async def test_get_member_accounts_not_found(client: AsyncClient):
    """GET /members/{id}/accounts returns 404 when member does not exist."""
    response = await client.get("/members/999999/accounts")
    assert response.status_code == 404
    assert response.json()["detail"] == "Member not found"


async def test_get_account_not_found(client: AsyncClient):
    """GET /accounts/{id} returns 404 when account does not exist."""
    response = await client.get("/accounts/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Account not found"


async def test_get_transactions_ok(client: AsyncClient, test_account):
    """GET /accounts/{id}/transactions returns 200 and list (may be empty)."""
    response = await client.get(f"/accounts/{test_account.id}/transactions")
    assert response.status_code == 200
    assert response.json() == []


async def test_get_transactions_account_not_found(client: AsyncClient):
    """GET /accounts/{id}/transactions returns 404 when account does not exist."""
    response = await client.get("/accounts/999999/transactions")
    assert response.status_code == 404
    assert response.json()["detail"] == "Account not found"


async def test_post_transaction_credit_ok(client: AsyncClient, test_account):
    """POST /accounts/{id}/transactions with CREDIT returns 200 and transaction."""
    response = await client.post(
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


async def test_post_transaction_debit_ok(client: AsyncClient, test_account):
    """POST /accounts/{id}/transactions with DEBIT (within balance) returns 200."""
    response = await client.post(
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


async def test_post_transaction_insufficient_funds(client: AsyncClient, test_account):
    """POST /accounts/{id}/transactions DEBIT over balance returns 400."""
    response = await client.post(
        f"/accounts/{test_account.id}/transactions",
        json={
            "amount": "200.00",
            "counterparty": "Store",
            "type": "DEBIT",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient funds"


async def test_post_transaction_account_not_found(client: AsyncClient):
    """POST /accounts/{id}/transactions returns 404 when account does not exist."""
    response = await client.post(
        "/accounts/999999/transactions",
        json={"amount": "10.00", "counterparty": "X", "type": "CREDIT"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Account not found"


async def test_post_transaction_validation_error(client: AsyncClient, test_account):
    """POST with invalid body returns 422."""
    response = await client.post(
        f"/accounts/{test_account.id}/transactions",
        json={"amount": "10.00", "type": "CREDIT"},
    )
    assert response.status_code == 422


async def test_patch_transaction_settle_ok(client: AsyncClient, test_account):
    """PATCH to SETTLED on a PENDING transaction returns 200."""
    create_resp = await client.post(
        f"/accounts/{test_account.id}/transactions",
        json={"amount": "10.00", "counterparty": "X", "type": "CREDIT"},
    )
    assert create_resp.status_code == 200
    tx_id = create_resp.json()["id"]

    response = await client.patch(
        f"/accounts/{test_account.id}/transactions/{tx_id}",
        json={"status": "SETTLED"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "SETTLED"


async def test_patch_transaction_fail_ok(client: AsyncClient, test_account):
    """PATCH to FAILED on a PENDING transaction returns 200."""
    create_resp = await client.post(
        f"/accounts/{test_account.id}/transactions",
        json={"amount": "10.00", "counterparty": "X", "type": "CREDIT"},
    )
    assert create_resp.status_code == 200
    tx_id = create_resp.json()["id"]

    response = await client.patch(
        f"/accounts/{test_account.id}/transactions/{tx_id}",
        json={"status": "FAILED"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "FAILED"


async def test_patch_transaction_not_found(client: AsyncClient, test_account):
    """PATCH when transaction does not exist returns 404."""
    response = await client.patch(
        f"/accounts/{test_account.id}/transactions/999999",
        json={"status": "SETTLED"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Transaction not found"


async def test_patch_transaction_invalid_transition(client: AsyncClient, test_account):
    """PATCH to SETTLED on already SETTLED transaction returns 400."""
    create_resp = await client.post(
        f"/accounts/{test_account.id}/transactions",
        json={"amount": "10.00", "counterparty": "X", "type": "CREDIT"},
    )
    assert create_resp.status_code == 200
    tx_id = create_resp.json()["id"]
    await client.patch(
        f"/accounts/{test_account.id}/transactions/{tx_id}",
        json={"status": "SETTLED"},
    )

    response = await client.patch(
        f"/accounts/{test_account.id}/transactions/{tx_id}",
        json={"status": "SETTLED"},
    )
    assert response.status_code == 400
    assert "not pending" in response.json()["detail"].lower() or "transition" in response.json()["detail"].lower()
