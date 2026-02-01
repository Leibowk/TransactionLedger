const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const DEFAULT_ACCOUNT_ID =
  import.meta.env.VITE_ACCOUNT_ID != null
    ? Number(import.meta.env.VITE_ACCOUNT_ID)
    : 1;

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
