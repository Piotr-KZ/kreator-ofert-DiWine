import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import CreateProject from "@/pages/CreateProject";
import LabLayout from "@/pages/LabLayout";
import Step3Kreator from "@/pages/Step3Kreator";
import Step4Tresci from "@/pages/Step4Tresci";
import Step5Wizualizacja from "@/pages/Step5Wizualizacja";

import OfferConfigurator from "@/pages/OfferConfigurator";
import OfferCostEstimate from "@/pages/OfferCostEstimate";
import OfferExport from "@/pages/OfferExport";
import CreateOffer from "@/pages/CreateOffer";
import OfferHome from "@/pages/OfferHome";
import OfferList from "@/pages/OfferList";
import OfferSettings from "@/pages/OfferSettings";
import OfferOrders from "@/pages/OfferOrders";
import OfferInvoices from "@/pages/OfferInvoices";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/offer" replace />} />
        <Route path="/offer" element={<OfferHome />} />
        <Route path="/offer/list" element={<OfferList />} />
        <Route path="/offer/orders" element={<OfferOrders />} />
        <Route path="/offer/invoices" element={<OfferInvoices />} />
        <Route path="/offer/settings" element={<OfferSettings />} />
        <Route path="/offer/create" element={<CreateOffer />} />
        <Route path="/offer/:offerId" element={<OfferConfigurator />} />
        <Route path="/offer/:offerId/cost" element={<OfferCostEstimate />} />
        <Route path="/offer/:offerId/export" element={<OfferExport />} />
        <Route path="/lab/create" element={<CreateProject />} />
        <Route path="/lab/:projectId" element={<LabLayout />}>
          <Route path="step/3" element={<Step3Kreator />} />
          <Route path="step/4" element={<Step4Tresci />} />
          <Route path="step/5" element={<Step5Wizualizacja />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
