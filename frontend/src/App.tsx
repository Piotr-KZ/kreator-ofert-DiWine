import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import CreateProject from "@/pages/CreateProject";
import LabLayout from "@/pages/LabLayout";
import Step1Brief from "@/pages/Step1Brief";
import Step2Validation from "@/pages/Step2Validation";

import Step3Kreator from "@/pages/Step3Kreator";
import Step4Tresci from "@/pages/Step4Tresci";
import Step5Wizualizacja from "@/pages/Step5Wizualizacja";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/lab/create" replace />} />
        <Route path="/lab/create" element={<CreateProject />} />
        <Route path="/lab/:projectId" element={<LabLayout />}>
          <Route path="step/1" element={<Step1Brief />} />
          <Route path="step/2" element={<Step2Validation />} />
          <Route path="step/3" element={<Step3Kreator />} />
          <Route path="step/4" element={<Step4Tresci />} />
          <Route path="step/5" element={<Step5Wizualizacja />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
