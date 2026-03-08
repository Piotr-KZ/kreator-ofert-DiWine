import { useEffect, useState } from "react";
import { superadminApi } from "../../api/superadmin";
import { Organization } from "../../types/models";
import { StatusBadge, SectionCard } from "@/components/ui";

interface OrganizationWithStats extends Organization {
  users_count?: number;
  subscriptions_count?: number;
}

export default function OrganizationsPage() {
  const [organizations, setOrganizations] = useState<OrganizationWithStats[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchOrganizations();
  }, []);

  const fetchOrganizations = async () => {
    setLoading(true);
    setError("");
    try {
      const { data } = await superadminApi.listOrganizations();
      setOrganizations(data.items || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to fetch organizations");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900">Organizations</h1>
      <p className="text-sm text-gray-500 mt-1 mb-6">
        Manage all organizations in the system
      </p>

      {/* Info banner */}
      <div className="flex items-start gap-3 p-4 bg-indigo-50 border border-indigo-200 rounded-xl mb-6">
        <svg className="w-5 h-5 text-indigo-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
        </svg>
        <div>
          <p className="text-sm font-medium text-indigo-800">Super Admin View</p>
          <p className="text-xs text-indigo-600">
            You are viewing all organizations across the entire platform. This view is only available to Super Admins.
          </p>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-700 text-sm rounded-lg">{error}</div>
      )}

      <SectionCard>
        <div className="overflow-x-auto -mx-6 -mb-6">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50">
                <th className="text-left px-4 py-3 font-medium text-gray-600">Organization</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Type</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Members</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Location</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Created</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={5} className="px-4 py-12 text-center text-gray-400">
                    <div className="flex justify-center">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600" />
                    </div>
                  </td>
                </tr>
              ) : organizations.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-12 text-center text-gray-400">
                    No organizations found
                  </td>
                </tr>
              ) : (
                organizations.map((org) => (
                  <tr key={org.id} className="border-b border-gray-100 hover:bg-gray-50/50">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <svg className="w-4 h-4 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                        </svg>
                        <div>
                          <div className="font-medium text-gray-900">{org.name}</div>
                          <div className="text-xs text-gray-400">{org.slug}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge variant={org.type === "business" ? "info" : "success"}>
                        {org.type?.toUpperCase()}
                      </StatusBadge>
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge variant="info">
                        {org.users_count || 0} members
                      </StatusBadge>
                    </td>
                    <td className="px-4 py-3 text-gray-500">
                      {org.billing_city}, {org.billing_country}
                    </td>
                    <td className="px-4 py-3 text-gray-500">
                      {new Date(org.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </SectionCard>
    </div>
  );
}
