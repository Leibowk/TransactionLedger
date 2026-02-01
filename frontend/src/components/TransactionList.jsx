import { useState } from "react";
import { updateTransactionStatus } from "../api/client";

function formatCurrency(value) {
  const num = typeof value === "string" ? parseFloat(value) : value;
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(num ?? 0);
}

function formatTimestamp(isoString) {
  if (!isoString) return "—";
  const d = new Date(isoString);
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(d);
}

function statusBadgeClass(status) {
  switch (status) {
    case "SETTLED":
      return "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300";
    case "PENDING":
      return "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300";
    case "FAILED":
      return "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300";
    default:
      return "bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-300";
  }
}

export function TransactionList({ transactions, accountId, onRefetch }) {
  const [actionTxId, setActionTxId] = useState(null);
  const [actionError, setActionError] = useState(null);

  const sorted = [...(transactions ?? [])].sort(
    (a, b) => new Date(b.timestamp) - new Date(a.timestamp)
  );

  async function handleStatusChange(txId, status) {
    if (!accountId || !onRefetch) return;
    setActionError(null);
    setActionTxId(txId);
    try {
      await updateTransactionStatus(accountId, txId, status);
      onRefetch();
    } catch (err) {
      setActionError(err.message || "Could not update status");
    } finally {
      setActionTxId(null);
    }
  }

  if (sorted.length === 0) {
    return (
      <section
        className="rounded-lg border border-slate-200 bg-white p-8 text-center shadow-sm dark:border-slate-700 dark:bg-slate-800"
        aria-label="Transaction ledger"
      >
        <p className="text-slate-500 dark:text-slate-400">No transactions yet.</p>
      </section>
    );
  }

  return (
    <section
      className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800"
      aria-label="Transaction ledger"
    >
      {actionError && (
        <p
          className="border-b border-red-200 bg-red-50 px-4 py-2 text-sm text-red-800 dark:border-red-800 dark:bg-red-900/20 dark:text-red-200"
          role="alert"
        >
          {actionError}
        </p>
      )}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-700">
          <thead className="bg-slate-50 dark:bg-slate-700/50">
            <tr>
              <th
                scope="col"
                className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400"
              >
                Date
              </th>
              <th
                scope="col"
                className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400"
              >
                Counterparty
              </th>
              <th
                scope="col"
                className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400"
              >
                Type
              </th>
              <th
                scope="col"
                className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400"
              >
                Status
              </th>
              <th
                scope="col"
                className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400"
              >
                Amount
              </th>
              {(accountId != null && onRefetch) && (
                <th
                  scope="col"
                  className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400"
                >
                  Actions
                </th>
              )}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
            {sorted.map((tx) => (
              <tr
                key={tx.id}
                className="bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700/50"
              >
                <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-700 dark:text-slate-300">
                  {formatTimestamp(tx.timestamp)}
                </td>
                <td className="whitespace-nowrap px-4 py-3 text-sm font-medium text-slate-900 dark:text-slate-100">
                  {tx.counterparty}
                </td>
                <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-700 dark:text-slate-300">
                  {tx.type === "CREDIT" ? "Credit" : "Debit"}
                </td>
                <td className="whitespace-nowrap px-4 py-3">
                  <span
                    className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${statusBadgeClass(tx.status)}`}
                  >
                    {tx.status}
                  </span>
                </td>
                <td
                  className={`whitespace-nowrap px-4 py-3 text-right text-sm font-medium ${
                    tx.type === "CREDIT"
                      ? "text-emerald-600 dark:text-emerald-400"
                      : "text-red-600 dark:text-red-400"
                  }`}
                >
                  {tx.type === "CREDIT" ? "+" : "−"}
                  {formatCurrency(tx.amount)}
                </td>
                {accountId != null && onRefetch && (
                  <td className="whitespace-nowrap px-4 py-3 text-right">
                    {tx.status === "PENDING" ? (
                      <span className="flex justify-end gap-1">
                        <button
                          type="button"
                          disabled={actionTxId === tx.id}
                          onClick={() => handleStatusChange(tx.id, "SETTLED")}
                          className="rounded border border-emerald-600 bg-emerald-600 px-2 py-1 text-xs font-medium text-white hover:bg-emerald-700 disabled:opacity-70 dark:border-emerald-500 dark:bg-emerald-500 dark:hover:bg-emerald-600"
                        >
                          Settle
                        </button>
                        <button
                          type="button"
                          disabled={actionTxId === tx.id}
                          onClick={() => handleStatusChange(tx.id, "FAILED")}
                          className="rounded border border-slate-300 px-2 py-1 text-xs font-medium text-slate-700 hover:bg-slate-100 dark:border-slate-600 dark:text-slate-200 dark:hover:bg-slate-600"
                        >
                          Fail
                        </button>
                      </span>
                    ) : (
                      <span className="text-slate-400">—</span>
                    )}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
