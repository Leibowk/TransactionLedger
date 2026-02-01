import { useState, useEffect, useCallback } from "react";
import { getAccount, getTransactions, DEFAULT_ACCOUNT_ID } from "../api/client";
import { AccountSummary } from "../components/AccountSummary";
import { TransactionList } from "../components/TransactionList";
import { CreateTransactionModal } from "../components/CreateTransactionModal";

export function AccountPage() {
  const [account, setAccount] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [createModalOpen, setCreateModalOpen] = useState(false);

  const accountId = DEFAULT_ACCOUNT_ID;

  const refetch = useCallback(async () => {
    try {
      const [accountData, transactionsData] = await Promise.all([
        getAccount(accountId),
        getTransactions(accountId),
      ]);
      setAccount(accountData);
      setTransactions(transactionsData ?? []);
    } catch (err) {
      setError(err.message || "Could not load account");
    }
  }, [accountId]);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        await refetch();
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
  }, [refetch]);

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
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
            Transaction history
          </h2>
          <button
            type="button"
            onClick={() => setCreateModalOpen(true)}
            className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 dark:bg-slate-100 dark:text-slate-900 dark:hover:bg-slate-200"
          >
            Create Transaction
          </button>
        </div>
        <TransactionList
          transactions={transactions}
          accountId={accountId}
          onRefetch={refetch}
        />
      </div>
      {createModalOpen && (
        <CreateTransactionModal
          accountId={accountId}
          onSuccess={() => {
            refetch();
            setCreateModalOpen(false);
          }}
          onClose={() => setCreateModalOpen(false)}
        />
      )}
    </div>
  );
}
