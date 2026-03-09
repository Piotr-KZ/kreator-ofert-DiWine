import { useState } from 'react';
import { Btn, Fld } from '@/components/ui';
import { gusApi, GUSData } from '@/api/gus';

interface GUSLookupProps {
  onResult: (data: GUSData) => void;
  onError?: (error: string) => void;
  initialNip?: string;
}

export default function GUSLookup({ onResult, onError, initialNip = '' }: GUSLookupProps) {
  const [nip, setNip] = useState(initialNip);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'error' | 'success'; text: string } | null>(null);

  const handleLookup = async () => {
    const clean = nip.replace(/[-\s]/g, '');
    if (clean.length !== 10 || !/^\d+$/.test(clean)) {
      setMessage({ type: 'error', text: 'NIP musi mieć 10 cyfr' });
      return;
    }

    setLoading(true);
    setMessage(null);
    try {
      const { data } = await gusApi.lookup(clean);
      onResult(data);
      setMessage({ type: 'success', text: `Pobrano dane: ${data.name}` });
    } catch (err: any) {
      const status = err.response?.status;
      const detail = err.response?.data?.detail;
      let msg = 'Błąd pobierania danych z GUS';
      if (status === 404) msg = 'Nie znaleziono firmy o podanym NIP';
      else if (status === 503) msg = 'GUS chwilowo niedostępny. Wpisz dane ręcznie.';
      else if (status === 429) msg = 'Zbyt wiele zapytań. Spróbuj za chwilę.';
      else if (detail) msg = detail;
      setMessage({ type: 'error', text: msg });
      onError?.(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="flex gap-2 items-end">
        <Fld
          label="NIP"
          placeholder="np. 526-104-08-28"
          value={nip}
          onChange={setNip}
          className="flex-1"
        />
        <Btn
          variant="ghost"
          onClick={handleLookup}
          loading={loading}
          className="whitespace-nowrap mb-0"
        >
          Pobierz z GUS
        </Btn>
      </div>
      {message && (
        <p className={`text-xs mt-1 ${message.type === 'error' ? 'text-red-500' : 'text-green-600'}`}>
          {message.text}
        </p>
      )}
    </div>
  );
}
