import { useEffect, useState } from "react";
import { usersApi } from "../api/users";
import { User } from "../types/models";
import { Btn, Fld, StatusBadge } from "@/components/ui";
import Modal from "@/components/shared/Modal";

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");

  // Edit modal
  const [editOpen, setEditOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [editForm, setEditForm] = useState({ full_name: "", email: "", is_superuser: false });
  const [editLoading, setEditLoading] = useState(false);

  // Delete confirm
  const [deleteId, setDeleteId] = useState<string | null>(null);

  useEffect(() => {
    fetchUsers();
  }, [page, pageSize, search]);

  const fetchUsers = async () => {
    setLoading(true);
    setError("");
    try {
      const { data } = await usersApi.list({ page, per_page: pageSize, search });
      setUsers(data.items || []);
      setTotal(data.total || 0);
    } catch (err: any) {
      if (err.response?.status !== 403) {
        setError(err.response?.data?.detail || "Failed to fetch users");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (user: User) => {
    setEditingUser(user);
    setEditForm({
      full_name: user.full_name || "",
      email: user.email || "",
      is_superuser: user.is_superuser || false,
    });
    setEditOpen(true);
  };

  const handleEditSubmit = async (ev: React.FormEvent) => {
    ev.preventDefault();
    if (!editingUser) return;
    setEditLoading(true);
    try {
      await usersApi.update(editingUser.id, editForm);
      setEditOpen(false);
      setEditingUser(null);
      fetchUsers();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to update user");
    } finally {
      setEditLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await usersApi.delete(id);
      setDeleteId(null);
      fetchUsers();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to delete user");
    }
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div>
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Users</h1>
        <div className="relative w-full sm:w-64">
          <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder="Search users..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            className="w-full pl-10 pr-4 py-2.5 border-2 border-gray-200 rounded-xl text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
          />
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-700 text-sm rounded-lg">{error}</div>
      )}

      {/* Table */}
      <div className="bg-white border-2 border-gray-200 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50">
                <th className="text-left px-4 py-3 font-medium text-gray-600">Name</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Super Admin</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Status</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Created</th>
                <th className="text-right px-4 py-3 font-medium text-gray-600">Actions</th>
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
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-12 text-center text-gray-400">
                    No users found
                  </td>
                </tr>
              ) : (
                users.map((u) => (
                  <tr key={u.id} className="border-b border-gray-100 hover:bg-gray-50/50">
                    <td className="px-4 py-3">
                      <div className="font-medium text-gray-900">{u.full_name || "N/A"}</div>
                      <div className="text-xs text-gray-400">{u.email}</div>
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge variant={u.is_superuser ? "error" : "neutral"}>
                        {u.is_superuser ? "YES" : "NO"}
                      </StatusBadge>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1.5">
                        <StatusBadge variant={u.is_active ? "success" : "error"}>
                          {u.is_active ? "Active" : "Inactive"}
                        </StatusBadge>
                        {u.is_verified && <StatusBadge variant="info">Verified</StatusBadge>}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-gray-500">
                      {new Date(u.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          onClick={() => handleEdit(u)}
                          className="px-2.5 py-1.5 text-xs text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => setDeleteId(u.id)}
                          className="px-2.5 py-1.5 text-xs text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200">
            <span className="text-sm text-gray-500">
              Total {total} users
            </span>
            <div className="flex items-center gap-1">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1.5 text-sm rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Prev
              </button>
              <span className="px-3 py-1.5 text-sm text-gray-600">
                {page} / {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-3 py-1.5 text-sm rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Edit Modal */}
      <Modal
        open={editOpen}
        onClose={() => { setEditOpen(false); setEditingUser(null); }}
        title="Edit User"
        footer={
          <>
            <Btn variant="ghost" onClick={() => { setEditOpen(false); setEditingUser(null); }}>
              Cancel
            </Btn>
            <Btn loading={editLoading} onClick={() => {
              const form = document.getElementById("edit-user-form") as HTMLFormElement;
              form?.requestSubmit();
            }}>
              Save
            </Btn>
          </>
        }
      >
        <form id="edit-user-form" onSubmit={handleEditSubmit} className="space-y-4">
          <Fld
            label="Full Name"
            value={editForm.full_name}
            onChange={(v) => setEditForm((f) => ({ ...f, full_name: v }))}
          />
          <Fld
            label="Email"
            type="email"
            value={editForm.email}
            onChange={(v) => setEditForm((f) => ({ ...f, email: v }))}
          />
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Super Admin
            </label>
            <select
              value={editForm.is_superuser ? "true" : "false"}
              onChange={(e) => setEditForm((f) => ({ ...f, is_superuser: e.target.value === "true" }))}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
            >
              <option value="false">No — Regular User</option>
              <option value="true">Yes — Super Admin (Global Access)</option>
            </select>
          </div>
        </form>
      </Modal>

      {/* Delete Confirm Modal */}
      <Modal
        open={!!deleteId}
        onClose={() => setDeleteId(null)}
        title="Delete User"
        footer={
          <>
            <Btn variant="ghost" onClick={() => setDeleteId(null)}>No</Btn>
            <Btn variant="danger" onClick={() => deleteId && handleDelete(deleteId)}>
              Yes, Delete
            </Btn>
          </>
        }
      >
        <p className="text-sm text-gray-600">
          Are you sure you want to delete this user? This action cannot be undone.
        </p>
      </Modal>
    </div>
  );
}
