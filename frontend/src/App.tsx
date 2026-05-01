import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import CreateProject from "@/pages/CreateProject";
import LabLayout from "@/pages/LabLayout";
import Step1Brief from "@/pages/Step1Brief";
import Step2Validation from "@/pages/Step2Validation";

import Step3Kreator from "@/pages/Step3Kreator";
import Step4Tresci from "@/pages/Step4Tresci";
import Step5Wizualizacja from "@/pages/Step5Wizualizacja";

import OfferConfigurator from "@/pages/OfferConfigurator";
import OfferContent from "@/pages/OfferContent";
import OfferSummary from "@/pages/OfferSummary";
import OfferExport from "@/pages/OfferExport";
import NewOffer from "@/pages/NewOffer";
import CreateOffer from "@/pages/CreateOffer";
import OfferHome from "@/pages/OfferHome";
import OfferList from "@/pages/OfferList";
import OfferSettings from "@/pages/OfferSettings";
import OfferOrders from "@/pages/OfferOrders";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/offer" replace />} />
        <Route path="/lab/create" element={<CreateProject />} />
        <Route path="/lab/:projectId" element={<LabLayout />}>
          <Route path="step/1" element={<Step1Brief />} />
          <Route path="step/2" element={<Step2Validation />} />
          <Route path="step/3" element={<Step3Kreator />} />
          <Route path="step/4" element={<Step4Tresci />} />
          <Route path="step/5" element={<Step5Wizualizacja />} />
        </Route>
        <Route path="/offer" element={<OfferHome />} />
        <Route path="/offer/list" element={<OfferList />} />
        <Route path="/offer/settings" element={<OfferSettings />} />
        <Route path="/offer/orders" element={<OfferOrders />} />
        <Route path="/offer/new" element={<NewOffer />} />
        <Route path="/offer/create" element={<CreateOffer />} />
        <Route path="/offer/:offerId" element={<OfferConfigurator />} />
        <Route path="/offer/:offerId/content" element={<OfferContent />} />
        <Route path="/offer/:offerId/summary" element={<OfferSummary />} />
        <Route path="/offer/:offerId/export" element={<OfferExport />} />
      </Routes>
    </BrowserRouter>
  );
}
