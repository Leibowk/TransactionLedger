import { useState, useEffect } from "react";
import { getAccount, getTransactions, DEFAULT_ACCOUNT_ID } from "../api/client";
import { AccountSummary } from "../components/AccountSummary";
import { TransactionList } from "../components/TransactionList";

export function AccountPage() {
  const [account, setAccount] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const accountId = DEFAULT_ACCOUNT_ID;

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [accountData, transactionsData] = await Promise.all([
          getAccount(accountId),
          getTransactions(accountId),
        ]);
        if (!cancelled) {
          setAccount(accountData);
          setTransactions(transactionsData ?? []);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message || "Could not load account");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [accountId]);

  if (loading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center p-8">
        <p className="text-slate-500 dark:text-slate-400">Loading…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mx-auto max-w-2xl p-8">
        <div
          className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800 dark:border-red-800 dark:bg-red-900/20 dark:text-red-200"
          role="alert"
        >
          <p className="font-medium">Could not load account</p>
          <p className="mt-1 text-sm">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl space-y-8 p-6">
      <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
        Transaction Ledger
      </h1>
      <AccountSummary account={account} />
      <div>
        <h2 className="mb-4 text-lg font-semibold text-slate-900 dark:text-slate-100">
          Transaction history
        </h2>
        <TransactionList transactions={transactions} />
      </div>
    </div>
  );
}
