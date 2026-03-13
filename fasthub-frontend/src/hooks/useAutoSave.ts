import { useEffect, useRef } from "react";

/**
 * Auto-save hook with debounce.
 * Calls saveFn after `delay` ms of inactivity when data changes.
 */
export function useAutoSave(
  data: unknown,
  saveFn: () => Promise<void>,
  delay = 2000,
) {
  const timeoutRef = useRef<ReturnType<typeof setTimeout>>();
  const isFirstRender = useRef(true);

  useEffect(() => {
    // Skip first render (initial load)
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }

    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(async () => {
      try {
        await saveFn();
      } catch (e) {
        console.error("Auto-save failed:", e);
      }
    }, delay);

    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [data, delay]);
}
