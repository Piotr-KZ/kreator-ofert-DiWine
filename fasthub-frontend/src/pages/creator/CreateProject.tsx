/**
 * CreateProject — simple modal/page to create a new project.
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Btn from "@/components/ui/Btn";
import Fld from "@/components/ui/Fld";
import { createProject } from "@/api/creator";

export default function CreateProject() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleCreate = async () => {
    if (!name.trim()) {
      setError("Podaj nazwę projektu");
      return;
    }
    setLoading(true);
    try {
      const { data } = await createProject(name.trim());
      navigate(`/creator/${data.id}/step/1`);
    } catch (e) {
      setError("Nie udało się utworzyć projektu");
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-lg p-8 w-full max-w-md">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Utwórz nową stronę</h1>
        <p className="text-sm text-gray-500 mb-6">
          Nadaj nazwę swojemu projektowi i rozpocznij tworzenie.
        </p>

        <Fld
          label="Nazwa strony"
          placeholder="np. Strona firmowa, Landing page..."
          value={name}
          onChange={setName}
          error={error}
        />

        <div className="flex gap-3 mt-6">
          <Btn variant="ghost" onClick={() => navigate("/panel")}>
            Anuluj
          </Btn>
          <Btn onClick={handleCreate} loading={loading} className="flex-1">
            Rozpocznij
          </Btn>
        </div>
      </div>
    </div>
  );
}
