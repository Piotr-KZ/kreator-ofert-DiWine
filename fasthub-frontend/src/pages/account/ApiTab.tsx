import { useEffect, useState } from 'react';
import { useOrgStore } from '@/store/orgStore';
import { apiTokensApi, webhooksApi, type ApiTokenInfo, type WebhookEndpoint } from '@/api/account';
import { Btn, Fld, SectionCard, StatusBadge, Chk } from '@/components/ui';
import Modal from '@/components/shared/Modal';

const WEBHOOK_EVENTS = [
  { key: 'form_submission', label: 'Nowe zgłoszenie z formularza' },
  { key: 'newsletter_signup', label: 'Zapis na newsletter' },
  { key: 'site_published', label: 'Strona opublikowana' },
  { key: 'site_updated', label: 'Strona zmodyfikowana' },
  { key: 'member_joined', label: 'Nowy członek zespołu' },
  { key: 'subscription_changed', label: 'Zmiana planu' },
  { key: 'payment_completed', label: 'Płatność zrealizowana' },
  { key: 'invoice_issued', label: 'Faktura wystawiona' },
];

const EXPIRY_OPTIONS = [
  { label: '30 dni', value: 30 },
  { label: '90 dni', value: 90 },
  { label: '1 rok', value: 365 },
  { label: 'Nigdy', value: 0 },
];

export default function ApiTab() {
  const { organization } = useOrgStore();

  // API Tokens
  const [tokens, setTokens] = useState<ApiTokenInfo[]>([]);
  const [tokensLoading, setTokensLoading] = useState(true);
  const [createModal, setCreateModal] = useState(false);
  const [tokenName, setTokenName] = useState('');
  const [tokenExpiry, setTokenExpiry] = useState(90);
  const [createLoading, setCreateLoading] = useState(false);
  const [newToken, setNewToken] = useState('');
  const [deleteTokenId, setDeleteTokenId] = useState<string | null>(null);

  // Webhooks
  const [webhooks, setWebhooks] = useState<WebhookEndpoint[]>([]);
  const [webhookUrl, setWebhookUrl] = useState('');
  const [webhookEvents, setWebhookEvents] = useState<string[]>([]);
  const [webhookLoading, setWebhookLoading] = useState(false);
  const [webhookMsg, setWebhookMsg] = useState('');
  const [testResult, setTestResult] = useState<{ success: boolean; status_code?: number } | null>(null);

  useEffect(() => {
    loadTokens();
    if (organization) loadWebhooks();
  }, [organization]);

  // === API Tokens ===
  const loadTokens = async () => {
    setTokensLoading(true);
    try {
      const data = await apiTokensApi.list();
      setTokens(Array.isArray(data) ? data : []);
    } catch { /* */ }
    finally { setTokensLoading(false); }
  };

  const createToken = async () => {
    setCreateLoading(true);
    try {
      const data = await apiTokensApi.create({
        name: tokenName,
        expires_in_days: tokenExpiry || undefined,
      });
      setNewToken(data.token || '');
      setTokenName('');
      await loadTokens();
    } catch { /* */ }
    finally { setCreateLoading(false); }
  };

  const deleteToken = async () => {
    if (!deleteTokenId) return;
    try {
      await apiTokensApi.remove(deleteTokenId);
      setTokens((prev) => prev.filter((t) => t.id !== deleteTokenId));
    } catch { /* */ }
    setDeleteTokenId(null);
  };

  // === Webhooks ===
  const loadWebhooks = async () => {
    if (!organization) return;
    try {
      const data = await webhooksApi.list(organization.id);
      setWebhooks(Array.isArray(data) ? data : []);
      if (data.length > 0) {
        setWebhookUrl(data[0].url || '');
        setWebhookEvents(data[0].events || []);
      }
    } catch { /* */ }
  };

  const toggleEvent = (event: string) => {
    setWebhookEvents((prev) =>
      prev.includes(event) ? prev.filter((e) => e !== event) : [...prev, event]
    );
  };

  const saveWebhook = async () => {
    if (!organization || !webhookUrl) return;
    setWebhookLoading(true);
    setWebhookMsg('');
    try {
      if (webhooks.length > 0) {
        await webhooksApi.update(organization.id, webhooks[0].id, {
          url: webhookUrl,
          events: webhookEvents,
        });
      } else {
        await webhooksApi.create(organization.id, {
          url: webhookUrl,
          events: webhookEvents,
        });
      }
      setWebhookMsg('Zapisano');
      await loadWebhooks();
    } catch {
      setWebhookMsg('Błąd zapisu');
    } finally {
      setWebhookLoading(false);
    }
  };

  const testWebhook = async () => {
    if (!organization || webhooks.length === 0) return;
    setTestResult(null);
    try {
      const result = await webhooksApi.test(organization.id, webhooks[0].id);
      setTestResult(result);
    } catch {
      setTestResult({ success: false });
    }
  };

  const activeWebhook = webhooks[0];

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900">API i webhook</h2>

      {/* API Keys */}
      <SectionCard title="Klucze API" desc="Klucze pozwalają na dostęp do API z zewnętrznych systemów.">
        <div className="mb-4">
          <Btn onClick={() => { setCreateModal(true); setNewToken(''); setTokenName(''); }}>
            Wygeneruj nowy klucz
          </Btn>
        </div>

        {tokensLoading ? (
          <div className="flex justify-center py-4">
            <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : tokens.length === 0 ? (
          <p className="text-sm text-gray-500">Brak kluczy API</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="pb-2 font-medium">Nazwa</th>
                  <th className="pb-2 font-medium">Utworzono</th>
                  <th className="pb-2 font-medium">Ostatnio użyty</th>
                  <th className="pb-2 font-medium">Akcja</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {tokens.map((t) => (
                  <tr key={t.id}>
                    <td className="py-2 font-medium text-gray-900">{t.name}</td>
                    <td className="py-2 text-gray-600">{new Date(t.created_at).toLocaleDateString('pl-PL')}</td>
                    <td className="py-2 text-gray-600">{t.last_used_at ? new Date(t.last_used_at).toLocaleDateString('pl-PL') : '-'}</td>
                    <td className="py-2">
                      <button onClick={() => setDeleteTokenId(t.id)} className="text-red-600 hover:text-red-700 text-sm font-medium">
                        Usuń
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </SectionCard>

      {/* Create Token Modal */}
      <Modal open={createModal} onClose={() => setCreateModal(false)} title="Nowy klucz API">
        {newToken ? (
          <div className="space-y-4">
            <p className="text-sm text-amber-600 font-medium">Zapisz klucz — nie będzie ponownie wyświetlony.</p>
            <div className="bg-gray-50 p-3 rounded-xl">
              <code className="text-sm font-mono break-all select-all">{newToken}</code>
            </div>
            <Btn onClick={() => { navigator.clipboard.writeText(newToken); }}>Kopiuj</Btn>
            <Btn variant="ghost" onClick={() => setCreateModal(false)}>Zamknij</Btn>
          </div>
        ) : (
          <div className="space-y-4">
            <Fld label="Nazwa klucza" value={tokenName} onChange={setTokenName} placeholder="np. Integracja z CRM" />
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Wygasa</label>
              <select
                value={tokenExpiry}
                onChange={(e) => setTokenExpiry(Number(e.target.value))}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-sm outline-none focus:border-indigo-400"
              >
                {EXPIRY_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>
            <Btn onClick={createToken} loading={createLoading} disabled={!tokenName}>Wygeneruj</Btn>
          </div>
        )}
      </Modal>

      {/* Delete Token Modal */}
      <Modal open={!!deleteTokenId} onClose={() => setDeleteTokenId(null)} title="Usuń klucz API">
        <div className="space-y-4">
          <p className="text-sm text-gray-600">Czy na pewno chcesz usunąć ten klucz? Wszystkie integracje używające tego klucza przestaną działać.</p>
          <div className="flex gap-3">
            <Btn variant="danger" onClick={deleteToken}>Usuń</Btn>
            <Btn variant="ghost" onClick={() => setDeleteTokenId(null)}>Anuluj</Btn>
          </div>
        </div>
      </Modal>

      {/* Webhook */}
      <SectionCard title="Webhook" desc="Webhook wysyła powiadomienia HTTP na Twój serwer gdy coś się dzieje.">
        <div className="space-y-4">
          <Fld label="Adres URL" type="url" value={webhookUrl} onChange={setWebhookUrl} placeholder="https://twojserwer.pl/webhook" />

          <div>
            <p className="text-sm font-medium text-gray-700 mb-2">Zdarzenia do subskrybowania:</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {WEBHOOK_EVENTS.map((ev) => (
                <Chk key={ev.key} on={webhookEvents.includes(ev.key)} onClick={() => toggleEvent(ev.key)}>
                  {ev.label}
                </Chk>
              ))}
            </div>
          </div>

          {activeWebhook && (
            <div className="flex items-center gap-3">
              <StatusBadge variant={activeWebhook.is_active ? 'success' : 'error'}>
                {activeWebhook.is_active ? 'Aktywny' : 'Nieaktywny'}
              </StatusBadge>
              {activeWebhook.last_triggered_at && (
                <span className="text-xs text-gray-500">
                  Ostatnio: {new Date(activeWebhook.last_triggered_at).toLocaleString('pl-PL')}
                </span>
              )}
            </div>
          )}

          <div className="flex gap-3">
            <Btn onClick={saveWebhook} loading={webhookLoading}>Zapisz webhook</Btn>
            {activeWebhook && (
              <Btn variant="ghost" onClick={testWebhook}>Wyślij test</Btn>
            )}
          </div>

          {webhookMsg && (
            <p className={`text-sm ${webhookMsg.includes('Błąd') ? 'text-red-600' : 'text-green-600'}`}>{webhookMsg}</p>
          )}

          {testResult && (
            <div className={`text-sm p-3 rounded-xl ${testResult.success ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
              {testResult.success ? 'Test pomyślny' : 'Test nieudany'}
              {testResult.status_code && ` (HTTP ${testResult.status_code})`}
            </div>
          )}
        </div>
      </SectionCard>

      {/* API Docs link */}
      <div className="bg-indigo-50 border border-indigo-200 rounded-xl p-6">
        <h3 className="text-sm font-semibold text-indigo-900 mb-1">Dokumentacja API</h3>
        <p className="text-sm text-indigo-700">
          Pełna dokumentacja API z przykładami i SDK dostępna jest w{' '}
          <a href="/api/docs" target="_blank" rel="noopener noreferrer" className="underline font-medium">
            panelu dokumentacji
          </a>.
        </p>
      </div>
    </div>
  );
}
