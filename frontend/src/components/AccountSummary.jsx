function formatCurrency(value) {
  const num = typeof value === "string" ? parseFloat(value) : value;
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(num ?? 0);
}

export function AccountSummary({ account, accounts, selectedAccountId, onAccountChange }) {
  if (!account) return null;

  return (
    <section
      className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800"
      aria-label="Account summary"
    >
      <h2 className="sr-only">Account summary</h2>
      <div className="space-y-4">
        {account.member && (
          <div>
            <p className="text-sm font-medium text-slate-500 dark:text-slate-400">
              Account holder
            </p>
            <p className="text-lg font-semibold text-slate-900 dark:text-slate-100">
              {account.member.first_name} {account.member.last_name}
            </p>
          </div>
        )}
        <div>
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">
            Account
          </p>
          {accounts && accounts.length > 0 ? (
            <select
              value={selectedAccountId ?? ""}
              onChange={(e) => onAccountChange?.(Number(e.target.value))}
              className="mt-1 block w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-900 shadow-sm focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100"
              aria-label="Select account"
            >
              {accounts.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name}
                </option>
              ))}
            </select>
          ) : (
            <p className="text-lg font-semibold text-slate-900 dark:text-slate-100">
              {account.name}
            </p>
          )}
        </div>
        <div>
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">
            Account number
          </p>
          <p className="font-mono text-slate-900 dark:text-slate-100">
            {account.masked_account_number}
          </p>
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <p className="text-sm font-medium text-slate-500 dark:text-slate-400">
              Available balance
            </p>
            <p className="text-xl font-semibold text-slate-900 dark:text-slate-100">
              {formatCurrency(account.available_balance)}
            </p>
          </div>
          <div>
            <p className="text-sm font-medium text-slate-500 dark:text-slate-400">
              Current balance
            </p>
            <p className="text-xl font-semibold text-slate-900 dark:text-slate-100">
              {formatCurrency(account.current_balance)}
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
