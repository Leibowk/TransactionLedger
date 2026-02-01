import { useState, useEffect } from "react";
import { createTransaction } from "../api/client";

export function CreateTransactionModal({ accountId, onSuccess, onClose }) {
  const [type, setType] = useState("CREDIT");
  const [amount, setAmount] = useState("");
  const [counterparty, setCounterparty] = useState("");
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    function handleEscape(e) {
      if (e.key === "Escape") onClose();
    }
    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [onClose]);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    const num = parseFloat(amount);
    if (Number.isNaN(num) || num < 0.01) {
      setError("Amount must be at least 0.01");
      return;
    }
    if (!counterparty.trim()) {
      setError("Counterparty is required");
      return;
    }
    setSubmitting(true);
    try {
      await createTransaction(accountId, {
        type,
        amount: num,
        counterparty: counterparty.trim(),
      });
      onSuccess();
      onClose();
    } catch (err) {
      setError(err.message || "Could not create transaction");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="create-transaction-title"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div
        className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl dark:bg-slate-800"
        onClick={(e) => e.stopPropagation()}
      >
        <h2
          id="create-transaction-title"
          className="text-xl font-semibold text-slate-900 dark:text-slate-100"
        >
          Create Transaction
        </h2>
        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          {error && (
            <p
              className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800 dark:border-red-800 dark:bg-red-900/20 dark:text-red-200"
              role="alert"
            >
              {error}
            </p>
          )}
          <div>
            <label
              htmlFor="create-type"
              className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
            >
              Type
            </label>
            <div id="create-type" className="flex gap-4 pt-1">
              <label className="flex cursor-pointer items-center gap-2">
                <input
                  type="radio"
                  name="type"
                  value="CREDIT"
                  checked={type === "CREDIT"}
                  onChange={() => setType("CREDIT")}
                  className="h-4 w-4 border-slate-300 text-slate-900 focus:ring-slate-500"
                />
                <span className="text-sm text-slate-700 dark:text-slate-300">
                  Credit
                </span>
              </label>
              <label className="flex cursor-pointer items-center gap-2">
                <input
                  type="radio"
                  name="type"
                  value="DEBIT"
                  checked={type === "DEBIT"}
                  onChange={() => setType("DEBIT")}
                  className="h-4 w-4 border-slate-300 text-slate-900 focus:ring-slate-500"
                />
                <span className="text-sm text-slate-700 dark:text-slate-300">
                  Debit
                </span>
              </label>
            </div>
          </div>
          <div>
            <label
              htmlFor="create-amount"
              className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
            >
              Amount
            </label>
            <input
              id="create-amount"
              type="number"
              step="0.01"
              min="0.01"
              required
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-900 shadow-sm focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100"
            />
          </div>
          <div>
            <label
              htmlFor="create-counterparty"
              className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
            >
              Counterparty
            </label>
            <input
              id="create-counterparty"
              type="text"
              required
              value={counterparty}
              onChange={(e) => setCounterparty(e.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-900 shadow-sm focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100"
            />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-200 dark:hover:bg-slate-600"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-70 dark:bg-slate-100 dark:text-slate-900 dark:hover:bg-slate-200"
            >
              {submitting ? "Sending…" : "Submit"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
