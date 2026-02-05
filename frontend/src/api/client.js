const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const DEFAULT_ACCOUNT_ID =
  import.meta.env.VITE_ACCOUNT_ID != null
    ? Number(import.meta.env.VITE_ACCOUNT_ID)
    : 1;

export const DEFAULT_MEMBER_ID =
  import.meta.env.VITE_MEMBER_ID != null
    ? Number(import.meta.env.VITE_MEMBER_ID)
    : 1;

export async function getAccountsByMember(memberId) {
  const res = await fetch(`${baseUrl}/members/${memberId}/accounts`);
  if (!res.ok) {
    throw new Error(res.status === 404 ? "Member not found" : "Could not load accounts");
  }
  return res.json();
}

export async function getAccount(accountId) {
  const res = await fetch(`${baseUrl}/accounts/${accountId}`);
  if (!res.ok) {
    throw new Error(res.status === 404 ? "Account not found" : "Could not load account");
  }
  return res.json();
}

export async function getTransactions(accountId) {
  const res = await fetch(`${baseUrl}/accounts/${accountId}/transactions`);
  if (!res.ok) {
    throw new Error("Could not load transactions");
  }
  return res.json();
}

export async function createTransaction(accountId, body) {
  const res = await fetch(`${baseUrl}/accounts/${accountId}/transactions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "Could not create transaction");
  }
  return res.json();
}

export async function updateTransactionStatus(accountId, transactionId, status) {
  const res = await fetch(
    `${baseUrl}/accounts/${accountId}/transactions/${transactionId}`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status }),
    }
  );
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "Could not update transaction status");
  }
  return res.json();
}
