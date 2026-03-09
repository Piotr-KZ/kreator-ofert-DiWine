import { useEffect, useState } from 'react';
import { useAuthStore } from '@/store/authStore';
import { authApi } from '@/api/auth';
import { twoFactorApi, sessionsApi, gdprApi, type SessionInfo } from '@/api/account';
import { Btn, Fld, SectionCard, StatusBadge } from '@/components/ui';
import Modal from '@/components/shared/Modal';

export default function SecurityTab() {
  const { user } = useAuthStore();

  // Change password
  const [curPwd, setCurPwd] = useState('');
  const [newPwd, setNewPwd] = useState('');
  const [confirmPwd, setConfirmPwd] = useState('');
  const [pwdLoading, setPwdLoading] = useState(false);
  const [pwdMsg, setPwdMsg] = useState('');
  const [pwdError, setPwdError] = useState('');

  // 2FA
  const [twoFaEnabled, setTwoFaEnabled] = useState(false);
  const [setupModal, setSetupModal] = useState(false);
  const [setupStep, setSetupStep] = useState(0);
  const [setupPwd, setSetupPwd] = useState('');
  const [qrCode, setQrCode] = useState('');
  const [manualKey, setManualKey] = useState('');
  const [totpCode, setTotpCode] = useState('');
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [setupLoading, setSetupLoading] = useState(false);
  const [setupError, setSetupError] = useState('');
  const [disableModal, setDisableModal] = useState(false);
  const [disablePwd, setDisablePwd] = useState('');
  const [disableCode, setDisableCode] = useState('');
  const [disableLoading, setDisableLoading] = useState(false);

  // Sessions
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [sessionsLoading, setSessionsLoading] = useState(true);

  // Delete account
  const [deleteModal, setDeleteModal] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState('');
  const [deleteLoading, setDeleteLoading] = useState(false);

  useEffect(() => {
    setTwoFaEnabled(!!(user as any)?.totp_enabled);
    loadSessions();
  }, [user]);

  const loadSessions = async () => {
    setSessionsLoading(true);
    try {
      const data = await sessionsApi.list();
      setSessions(Array.isArray(data) ? data : []);
    } catch {
      // Sessions endpoint may not be available
    } finally {
      setSessionsLoading(false);
    }
  };

  // === Change Password ===
  const changePassword = async () => {
    setPwdError('');
    setPwdMsg('');
    if (newPwd !== confirmPwd) { setPwdError('Hasła nie pasują'); return; }
    if (newPwd.length < 8) { setPwdError('Hasło musi mieć min. 8 znaków'); return; }
    setPwdLoading(true);
    try {
      await authApi.changePassword(curPwd, newPwd);
      setPwdMsg('Hasło zmienione');
      setCurPwd(''); setNewPwd(''); setConfirmPwd('');
    } catch (err: any) {
      setPwdError(err.response?.data?.detail || 'Błąd zmiany hasła');
    } finally {
      setPwdLoading(false);
    }
  };

  // === 2FA Setup ===
  const startSetup = async () => {
    setSetupError('');
    setSetupLoading(true);
    try {
      const data = await twoFactorApi.setup(setupPwd);
      setQrCode(data.qr_code || '');
      setManualKey(data.secret || '');
      setSetupStep(1);
    } catch (err: any) {
      setSetupError(err.response?.data?.detail || 'Błąd weryfikacji hasła');
    } finally {
      setSetupLoading(false);
    }
  };

  const verifySetup = async () => {
    setSetupError('');
    setSetupLoading(true);
    try {
      const data = await twoFactorApi.verify(totpCode);
      setBackupCodes(data.backup_codes || []);
      setSetupStep(2);
      setTwoFaEnabled(true);
    } catch (err: any) {
      setSetupError(err.response?.data?.detail || 'Nieprawidłowy kod');
    } finally {
      setSetupLoading(false);
    }
  };

  const disable2FA = async () => {
    setDisableLoading(true);
    try {
      await twoFactorApi.disable(disablePwd, disableCode);
      setTwoFaEnabled(false);
      setDisableModal(false);
      setDisablePwd(''); setDisableCode('');
    } catch {
      // Error
    } finally {
      setDisableLoading(false);
    }
  };

  // === Sessions ===
  const revokeSession = async (id: string) => {
    try {
      await sessionsApi.revoke(id);
      setSessions((prev) => prev.filter((s) => s.id !== id));
    } catch { /* */ }
  };

  const revokeAll = async () => {
    try {
      await sessionsApi.revokeAll();
      await loadSessions();
    } catch { /* */ }
  };

  // === Delete Account ===
  const handleDelete = async () => {
    if (deleteConfirm !== 'USUŃ') return;
    setDeleteLoading(true);
    try {
      await gdprApi.requestDeletion();
      setDeleteModal(false);
    } catch { /* */ }
    finally { setDeleteLoading(false); }
  };

  const deviceIcon = (type: string) => {
    if (type === 'mobile') return '📱';
    if (type === 'tablet') return '📱';
    return '💻';
  };

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900">Bezpieczeństwo</h2>

      {/* Change Password */}
      <SectionCard title="Zmień hasło">
        <div className="space-y-4">
          <Fld label="Obecne hasło" type="password" value={curPwd} onChange={setCurPwd} />
          <Fld label="Nowe hasło" type="password" value={newPwd} onChange={setNewPwd} placeholder="Min. 8 znaków" />
          <Fld label="Powtórz nowe hasło" type="password" value={confirmPwd} onChange={setConfirmPwd} />
          <div className="text-xs text-gray-500 space-y-1">
            <p className={newPwd.length >= 8 ? 'text-green-600' : ''}>Min. 8 znaków</p>
            <p className={/[A-Z]/.test(newPwd) ? 'text-green-600' : ''}>Wielka litera</p>
            <p className={/[a-z]/.test(newPwd) ? 'text-green-600' : ''}>Mała litera</p>
            <p className={/[0-9]/.test(newPwd) ? 'text-green-600' : ''}>Cyfra</p>
          </div>
          {pwdError && <p className="text-sm text-red-600">{pwdError}</p>}
          {pwdMsg && <p className="text-sm text-green-600">{pwdMsg}</p>}
          <Btn onClick={changePassword} loading={pwdLoading}>Zmień hasło</Btn>
        </div>
      </SectionCard>

      {/* 2FA */}
      <SectionCard title="Weryfikacja dwuetapowa (2FA)">
        {twoFaEnabled ? (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <StatusBadge variant="success">2FA aktywne</StatusBadge>
            </div>
            <div className="flex gap-3">
              <Btn variant="danger" onClick={() => setDisableModal(true)}>Wyłącz 2FA</Btn>
              <Btn variant="ghost" onClick={() => { setSetupModal(true); setSetupStep(0); }}>
                Wygeneruj nowe kody zapasowe
              </Btn>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            <p className="text-sm text-gray-600">
              Dodaj dodatkową warstwę ochrony. Po włączeniu przy każdym logowaniu będziesz potrzebować kodu z aplikacji.
            </p>
            <Btn onClick={() => { setSetupModal(true); setSetupStep(0); setSetupPwd(''); setTotpCode(''); setSetupError(''); }}>
              Włącz 2FA
            </Btn>
          </div>
        )}
      </SectionCard>

      {/* 2FA Setup Modal */}
      <Modal open={setupModal} onClose={() => setSetupModal(false)} title="Konfiguracja 2FA">
        {setupStep === 0 && (
          <div className="space-y-4">
            <Fld label="Potwierdź hasło" type="password" value={setupPwd} onChange={setSetupPwd} />
            {setupError && <p className="text-sm text-red-600">{setupError}</p>}
            <Btn onClick={startSetup} loading={setupLoading}>Dalej</Btn>
          </div>
        )}
        {setupStep === 1 && (
          <div className="space-y-4">
            {qrCode && (
              <div className="flex justify-center">
                <img src={`data:image/png;base64,${qrCode}`} alt="QR Code" className="w-48 h-48" />
              </div>
            )}
            {manualKey && (
              <div className="text-center">
                <p className="text-xs text-gray-500 mb-1">Lub wpisz ręcznie:</p>
                <code className="text-sm bg-gray-100 px-3 py-1 rounded font-mono select-all">{manualKey}</code>
              </div>
            )}
            <p className="text-sm text-gray-600">
              Zeskanuj kod w Google Authenticator, Authy lub innej aplikacji TOTP.
            </p>
            <Fld label="Wpisz 6-cyfrowy kod z aplikacji" value={totpCode} onChange={setTotpCode} placeholder="000000" />
            {setupError && <p className="text-sm text-red-600">{setupError}</p>}
            <Btn onClick={verifySetup} loading={setupLoading}>Aktywuj</Btn>
          </div>
        )}
        {setupStep === 2 && (
          <div className="space-y-4">
            <p className="text-sm font-medium text-gray-900">Kody zapasowe</p>
            <p className="text-sm text-amber-600">
              Zapisz te kody w bezpiecznym miejscu. Każdy kod działa tylko raz.
            </p>
            <div className="grid grid-cols-2 gap-2 bg-gray-50 p-4 rounded-xl">
              {backupCodes.map((code, i) => (
                <code key={i} className="text-sm font-mono text-gray-800">{code}</code>
              ))}
            </div>
            <Btn onClick={() => setSetupModal(false)}>Potwierdzam — zapisałem kody</Btn>
          </div>
        )}
      </Modal>

      {/* Disable 2FA Modal */}
      <Modal open={disableModal} onClose={() => setDisableModal(false)} title="Wyłącz 2FA">
        <div className="space-y-4">
          <Fld label="Hasło" type="password" value={disablePwd} onChange={setDisablePwd} />
          <Fld label="Kod TOTP" value={disableCode} onChange={setDisableCode} placeholder="000000" />
          <Btn variant="danger" onClick={disable2FA} loading={disableLoading}>Wyłącz 2FA</Btn>
        </div>
      </Modal>

      {/* Sessions */}
      <SectionCard title="Aktywne sesje">
        {sessionsLoading ? (
          <div className="flex justify-center py-4">
            <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : sessions.length === 0 ? (
          <p className="text-sm text-gray-500">Brak danych o sesjach</p>
        ) : (
          <div className="space-y-3">
            {sessions.map((s) => (
              <div key={s.id} className="flex items-center justify-between py-2 border-b last:border-0">
                <div className="flex items-center gap-3">
                  <span className="text-xl">{deviceIcon(s.device_type)}</span>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{s.device_name || `${s.browser} na ${s.os}`}</p>
                    <p className="text-xs text-gray-500">IP: {s.ip_address} — {new Date(s.last_active_at).toLocaleDateString('pl-PL')}</p>
                  </div>
                </div>
                {s.is_current ? (
                  <StatusBadge variant="info">Ta sesja</StatusBadge>
                ) : (
                  <Btn variant="ghost" onClick={() => revokeSession(s.id)}>
                    <span className="text-red-600 text-sm">Wyloguj</span>
                  </Btn>
                )}
              </div>
            ))}
          </div>
        )}
        {sessions.length > 1 && (
          <div className="mt-4">
            <Btn variant="danger" onClick={revokeAll}>Wyloguj ze wszystkich urządzeń</Btn>
          </div>
        )}
      </SectionCard>

      {/* Delete Account */}
      <SectionCard className="!border-red-200" title="Usunięcie konta">
        <p className="text-sm text-gray-600 mb-4">
          Po usunięciu konta masz 14 dni na zmianę decyzji. Twoje dane zostaną wyeksportowane i wysłane na email, a następnie zanonimizowane.
        </p>
        <Btn variant="danger" onClick={() => setDeleteModal(true)}>Usuń moje konto</Btn>
      </SectionCard>

      <Modal open={deleteModal} onClose={() => setDeleteModal(false)} title="Usunięcie konta">
        <div className="space-y-4">
          <p className="text-sm text-gray-600">Wpisz <strong>USUŃ</strong> aby potwierdzić.</p>
          <Fld value={deleteConfirm} onChange={setDeleteConfirm} placeholder="USUŃ" />
          <Btn variant="danger" onClick={handleDelete} loading={deleteLoading} disabled={deleteConfirm !== 'USUŃ'}>
            Potwierdź usunięcie
          </Btn>
        </div>
      </Modal>
    </div>
  );
}
