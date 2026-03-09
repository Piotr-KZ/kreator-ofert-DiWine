import { useEffect, useState } from 'react';
import { Btn, SectionCard, Toggle } from '@/components/ui';
import { notificationsApi } from '@/api/account';

interface NotifRow {
  key: string;
  label: string;
  alwaysOn: boolean;
}

const NOTIFICATION_TYPES: NotifRow[] = [
  { key: 'form_submission', label: 'Nowe zgłoszenie z formularza', alwaysOn: false },
  { key: 'newsletter_signup', label: 'Zapis na newsletter', alwaysOn: false },
  { key: 'payment_completed', label: 'Płatność zrealizowana', alwaysOn: false },
  { key: 'payment_failed', label: 'Płatność nieudana', alwaysOn: true },
  { key: 'security_alerts', label: 'Alerty bezpieczeństwa', alwaysOn: true },
  { key: 'team_changes', label: 'Zmiany w zespole', alwaysOn: false },
  { key: 'system_updates', label: 'Aktualizacje systemu', alwaysOn: false },
];

export default function NotificationsTab() {
  const [prefs, setPrefs] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');

  useEffect(() => {
    loadPreferences();
  }, []);

  const loadPreferences = async () => {
    setLoading(true);
    try {
      const data = await notificationsApi.getPreferences();
      setPrefs(data as any);
    } catch {
      // Set defaults
      const defaults: Record<string, boolean> = {};
      NOTIFICATION_TYPES.forEach((t) => {
        defaults[`${t.key}_email`] = true;
        defaults[`${t.key}_app`] = true;
      });
      setPrefs(defaults);
    } finally {
      setLoading(false);
    }
  };

  const toggle = (key: string) => {
    setPrefs((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const save = async () => {
    setSaving(true);
    setMsg('');
    try {
      await notificationsApi.updatePreferences(prefs as any);
      setMsg('Zapisano');
    } catch {
      setMsg('Błąd zapisu');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900">Powiadomienia</h2>

      <SectionCard title="Preferencje powiadomień" desc="Wybierz jakie powiadomienia chcesz otrzymywać i jakimi kanałami.">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="pb-2 font-medium">Typ</th>
                <th className="pb-2 font-medium text-center">Email</th>
                <th className="pb-2 font-medium text-center">W aplikacji</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {NOTIFICATION_TYPES.map((t) => (
                <tr key={t.key}>
                  <td className="py-3 text-gray-700">{t.label}</td>
                  <td className="py-3 text-center">
                    <div className="flex justify-center">
                      <Toggle
                        on={t.alwaysOn ? true : !!prefs[`${t.key}_email`]}
                        onClick={t.alwaysOn ? undefined : () => toggle(`${t.key}_email`)}
                      />
                    </div>
                  </td>
                  <td className="py-3 text-center">
                    <div className="flex justify-center">
                      <Toggle
                        on={t.alwaysOn ? true : !!prefs[`${t.key}_app`]}
                        onClick={t.alwaysOn ? undefined : () => toggle(`${t.key}_app`)}
                      />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {msg && (
          <p className={`text-sm mt-4 ${msg.includes('Błąd') ? 'text-red-600' : 'text-green-600'}`}>{msg}</p>
        )}
        <div className="mt-4">
          <Btn onClick={save} loading={saving}>Zapisz preferencje</Btn>
        </div>
      </SectionCard>
    </div>
  );
}
