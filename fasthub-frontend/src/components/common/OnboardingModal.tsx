import { useState } from "react";
import axios from "axios";
import Modal from "@/components/shared/Modal";
import { Btn, Fld } from "@/components/ui";
import { APP_CONFIG } from "@/config/app.config";

interface OnboardingModalProps {
  visible: boolean;
  organizationId: number;
  organizationName: string;
  onComplete: () => void;
  onSkip: () => void;
}

export default function OnboardingModal({
  visible,
  organizationId,
  organizationName,
  onComplete,
  onSkip,
}: OnboardingModalProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [orgType, setOrgType] = useState<"business" | "individual">("business");
  const [form, setForm] = useState({
    org_name: organizationName,
    nip: "",
    phone: "",
    billing_street: "",
    billing_city: "",
    billing_postal_code: "",
    billing_country: "Poland",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const set = (key: string) => (val: string) =>
    setForm((f) => ({ ...f, [key]: val }));

  const validate = () => {
    const e: Record<string, string> = {};
    if (!form.org_name.trim()) e.org_name = "Organization name is required";
    if (orgType === "business" && form.nip && !/^\d{10}$|^\d{3}-\d{3}-\d{2}-\d{2}$|^\d{3}-?\d{2}-?\d{2}-?\d{3}$/.test(form.nip))
      e.nip = "NIP must be 10 digits (e.g., 1234567890 or 123-456-78-90)";
    if (form.phone && !/^[\d\s\-+()]{9,20}$/.test(form.phone))
      e.phone = "Phone must be 9-15 digits (e.g., +48 123 456 789)";
    if (!form.billing_street.trim()) e.billing_street = "Street address is required";
    if (!form.billing_city.trim()) e.billing_city = "City is required";
    if (!form.billing_postal_code.trim()) e.billing_postal_code = "Postal code is required";
    else if (!/^\d{2}-?\d{3}$/.test(form.billing_postal_code))
      e.billing_postal_code = "Postal code must be 5 digits (e.g., 00-001)";
    if (!form.billing_country.trim()) e.billing_country = "Country is required";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (ev: React.FormEvent) => {
    ev.preventDefault();
    if (!validate()) return;

    setLoading(true);
    setError("");
    try {
      const token = localStorage.getItem("access_token");
      await axios.patch(
        `${APP_CONFIG.api.baseUrl}/organizations/${organizationId}/complete`,
        {
          name: form.org_name,
          type: orgType,
          nip: form.nip || null,
          phone: form.phone || null,
          billing_street: form.billing_street,
          billing_city: form.billing_city,
          billing_postal_code: form.billing_postal_code,
          billing_country: form.billing_country,
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      onComplete();
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setError(detail.map((e: any) => e.msg || "Validation error").join(", "));
      } else {
        setError(detail || "Failed to complete organization profile");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal open={visible} onClose={() => {}} title="Complete Your Organization Profile">
      <p className="text-sm text-gray-500 mb-6">
        Add your organization details to unlock all features
      </p>

      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-700 text-sm rounded-lg">{error}</div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <Fld
          label="Organization Name"
          value={form.org_name}
          onChange={set("org_name")}
          error={errors.org_name}
        />

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            Organization Type
          </label>
          <select
            value={orgType}
            onChange={(e) => setOrgType(e.target.value as "business" | "individual")}
            className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-sm outline-none transition-all focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
          >
            <option value="business">Business</option>
            <option value="individual">Individual</option>
          </select>
        </div>

        {orgType === "business" && (
          <Fld
            label="NIP (Tax ID)"
            value={form.nip}
            onChange={set("nip")}
            placeholder="1234567890 or 123-456-78-90"
            error={errors.nip}
          />
        )}

        <Fld
          label="Phone"
          type="tel"
          value={form.phone}
          onChange={set("phone")}
          placeholder="+48 123 456 789"
          error={errors.phone}
        />

        <h4 className="font-semibold text-gray-900 pt-2">Billing Address</h4>

        <Fld
          label="Street Address"
          value={form.billing_street}
          onChange={set("billing_street")}
          placeholder="ul. Przykładowa 123"
          error={errors.billing_street}
        />

        <div className="grid grid-cols-2 gap-4">
          <Fld
            label="City"
            value={form.billing_city}
            onChange={set("billing_city")}
            placeholder="Warsaw"
            error={errors.billing_city}
          />
          <Fld
            label="Postal Code"
            value={form.billing_postal_code}
            onChange={set("billing_postal_code")}
            placeholder="00-001"
            error={errors.billing_postal_code}
          />
        </div>

        <Fld
          label="Country"
          value={form.billing_country}
          onChange={set("billing_country")}
          placeholder="Poland"
          error={errors.billing_country}
        />

        <div className="flex gap-3 pt-4">
          <Btn variant="ghost" onClick={onSkip} className="flex-1">
            Skip for now
          </Btn>
          <Btn type="submit" loading={loading} className="flex-1">
            Complete Profile
          </Btn>
        </div>

        <p className="text-center text-xs text-gray-400">
          You can complete this later in Settings
        </p>
      </form>
    </Modal>
  );
}
