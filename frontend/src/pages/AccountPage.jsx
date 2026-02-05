import { useState, useEffect, useCallback } from "react";
import {
  getAccount,
  getAccountsByMember,
  getTransactions,
  DEFAULT_MEMBER_ID,
} from "../api/client";
import { AccountSummary } from "../components/AccountSummary";
import { TransactionList } from "../components/TransactionList";
import { CreateTransactionModal } from "../components/CreateTransactionModal";

export function AccountPage() {
  const [accounts, setAccounts] = useState([]);
  const [selectedAccountId, setSelectedAccountId] = useState(null);
  const [account, setAccount] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [createModalOpen, setCreateModalOpen] = useState(false);

  const memberId = DEFAULT_MEMBER_ID;

  const refetch = useCallback(async () => {
    if (!selectedAccountId) return;
    try {
      const [accountData, transactionsData] = await Promise.all([
        getAccount(selectedAccountId),
        getTransactions(selectedAccountId),
      ]);
      setAccount(accountData);
      setTransactions(transactionsData ?? []);
    } catch (err) {
      setError(err.message || "Could not load account");
    }
  }, [selectedAccountId]);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    getAccountsByMember(memberId)
      .then((list) => {
        if (!cancelled) {
          setAccounts(list);
          setSelectedAccountId(list[0]?.id ?? null);
          if (list.length === 0) setLoading(false);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err.message || "Could not load accounts");
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [memberId]);

  useEffect(() => {
    if (selectedAccountId == null) return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    Promise.all([
      getAccount(selectedAccountId),
      getTransactions(selectedAccountId),
    ])
      .then(([accountData, transactionsData]) => {
        if (!cancelled) {
          setAccount(accountData);
          setTransactions(transactionsData ?? []);
        }
      })
      .catch((err) => {
        if (!cancelled) setError(err.message || "Could not load account");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [selectedAccountId]);

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

  if (accounts.length === 0) {
    return (
      <div className="mx-auto max-w-2xl p-8">
        <div
          className="rounded-lg border border-slate-200 bg-white p-6 text-center dark:border-slate-700 dark:bg-slate-800"
          role="alert"
        >
          <p className="text-slate-600 dark:text-slate-300">No accounts found.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl space-y-8 p-6">
      <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
        Transaction Ledger
      </h1>
      <AccountSummary
        account={account}
        accounts={accounts}
        selectedAccountId={selectedAccountId}
        onAccountChange={setSelectedAccountId}
      />
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
          accountId={selectedAccountId}
          onRefetch={refetch}
        />
      </div>
      {createModalOpen && (
        <CreateTransactionModal
          accountId={selectedAccountId}
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
