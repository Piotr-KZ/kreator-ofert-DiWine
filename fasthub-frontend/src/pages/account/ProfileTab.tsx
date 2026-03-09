import { useEffect, useState } from 'react';
import { useAuthStore } from '@/store/authStore';
import { usersApi } from '@/api/users';
import { Btn, Fld, SectionCard } from '@/components/ui';

const languages = ['Polski', 'English', 'Deutsch'];
const timezones = ['Europe/Warsaw', 'Europe/Berlin', 'Europe/London', 'Europe/Paris', 'UTC', 'America/New_York'];

export default function ProfileTab() {
  const { user, fetchCurrentUser } = useAuthStore();
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [position, setPosition] = useState('');
  const [language, setLanguage] = useState('Polski');
  const [timezone, setTimezone] = useState('Europe/Warsaw');
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState('');
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState('');

  useEffect(() => {
    if (user) {
      setFullName(user.full_name || '');
      setPhone(user.phone || '');
      setPosition(user.position || '');
      setLanguage(user.language || 'Polski');
      setTimezone(user.timezone || 'Europe/Warsaw');
      setAvatarPreview(user.avatar_url || '');
    }
  }, [user]);

  const initials = (user?.full_name || 'U')
    .split(' ')
    .map((w) => w[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setAvatarFile(file);
    setAvatarPreview(URL.createObjectURL(file));
  };

  const saveProfile = async () => {
    setLoading(true);
    setMsg('');
    try {
      if (avatarFile) {
        await usersApi.uploadAvatar(avatarFile);
      }
      await usersApi.updateMe({ full_name: fullName, phone, position, language, timezone });
      await fetchCurrentUser();
      setMsg('Zapisano');
      setAvatarFile(null);
    } catch {
      setMsg('Błąd podczas zapisu');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900">Profil</h2>

      <SectionCard title="Dane osobowe">
        <div className="space-y-4">
          <div className="flex items-center gap-4">
            {avatarPreview ? (
              <img src={avatarPreview} alt="Avatar" className="w-16 h-16 rounded-full object-cover" />
            ) : (
              <div className="w-16 h-16 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 font-bold text-lg">
                {initials}
              </div>
            )}
            <label className="cursor-pointer">
              <span className="text-sm text-indigo-600 hover:text-indigo-700 font-medium">Zmień zdjęcie</span>
              <input type="file" accept="image/*" className="hidden" onChange={handleAvatarChange} />
            </label>
          </div>
          <Fld label="Imię i nazwisko" value={fullName} onChange={setFullName} />
          <Fld label="Email" value={user?.email || ''} disabled />
          <Fld label="Telefon" type="tel" value={phone} onChange={setPhone} placeholder="+48 123 456 789" />
          <Fld label="Stanowisko" value={position} onChange={setPosition} placeholder="np. CEO, Developer" />
        </div>
      </SectionCard>

      <SectionCard title="Preferencje">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">Język interfejsu</label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
            >
              {languages.map((l) => (
                <option key={l} value={l}>{l}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">Strefa czasowa</label>
            <select
              value={timezone}
              onChange={(e) => setTimezone(e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
            >
              {timezones.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
        </div>
      </SectionCard>

      {msg && (
        <p className={`text-sm ${msg.includes('Błąd') ? 'text-red-600' : 'text-green-600'}`}>{msg}</p>
      )}
      <Btn onClick={saveProfile} loading={loading}>Zapisz zmiany</Btn>
    </div>
  );
}
