import { useState, useCallback } from "react";

import { ApiError } from "../api/client";

export function useApi<TResp, TArgs extends unknown[]>(fn: (...args: TArgs) => Promise<TResp>) {
  const [data, setData] = useState<TResp | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  const run = useCallback(
    async (...args: TArgs) => {
      setPending(true);
      setError(null);
      try {
        const result = await fn(...args);
        setData(result);
        return result;
      } catch (e) {
        if (e instanceof ApiError) setError(e.message);
        else if (e instanceof Error) setError(e.message);
        else setError("Unexpected error");
        return null;
      } finally {
        setPending(false);
      }
    },
    [fn],
  );

  function reset() {
    setData(null);
    setError(null);
  }

  return { data, error, pending, run, reset, setData };
}
