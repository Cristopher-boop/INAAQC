// src/App.tsx
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import SignIn from "./pages/AuthPages/SignIn";
import SignUp from "./pages/AuthPages/SignUp";
import NotFound from "./pages/OtherPage/NotFound";
import UserProfiles from "./pages/UserProfiles";
import Videos from "./pages/UiElements/Videos";
import Images from "./pages/UiElements/Images";
import Alerts from "./pages/UiElements/Alerts";
import Badges from "./pages/UiElements/Badges";
import Avatars from "./pages/UiElements/Avatars";
import Buttons from "./pages/UiElements/Buttons";
import LineChart from "./pages/Charts/LineChart";
import BarChart from "./pages/Charts/BarChart";
import Calendar from "./pages/Calendar";
import BasicTables from "./pages/Tables/BasicTables";
import FormElements from "./pages/Forms/FormElements";
import Blank from "./pages/Blank";
import AppLayout from "./layout/AppLayout";
import { ScrollToTop } from "./components/common/ScrollToTop";
import Home from "./pages/Dashboard/Home";

export default function App() {
  return (
    <>
      <Router>
        <ScrollToTop />
        <Routes>
          {/* Dashboard Layout */}
          <Route element={<AppLayout />}>
            <Route index path="/" element={<Home />} />

            {/* Others Page */}
            <Route path="/profile" element={<UserProfiles />} />
            <Route path="/calendar" element={<Calendar />} />
            <Route path="/blank" element={<Blank />} />

            {/* Forms */}
            <Route path="/form-elements" element={<FormElements />} />

            {/* Tables */}
            <Route path="/basic-tables" element={<BasicTables />} />

            {/* Ui Elements */}
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/avatars" element={<Avatars />} />
            <Route path="/badge" element={<Badges />} />
            <Route path="/buttons" element={<Buttons />} />
            <Route path="/images" element={<Images />} />
            <Route path="/videos" element={<Videos />} />

            {/* Charts */}
            <Route path="/line-chart" element={<LineChart />} />
            <Route path="/bar-chart" element={<BarChart />} />

            {/* Usuarios */}
            <Route path="/usuarios/analistas" element={<UsuariosPage rol="analista" />} />
            <Route path="/usuarios/doctores" element={<UsuariosPage rol="doctor" />} />
            <Route path="/usuarios/ti" element={<UsuariosPage rol="TI" />} />

            {/* Roles */}
            <Route path="/roles" element={<RolesPage />} />

            {/* Pacientes */}
            <Route path="/pacientes" element={<PacientesPage />} />

            {/* Archivos */}
            <Route path="/archivos" element={<ArchivosPage />} />

            {/* Tipos Observacion */}
            <Route path="/tipos-observacion" element={<TiposObservacionPage />} />

            {/* Admisiones */}
            <Route path="/admisiones" element={<AdmisionesPage />} />

            {/* OCR Crudo */}
            <Route path="/ocr-crudo" element={<OcrPage />} />

            {/* Observaciones */}
            <Route path="/observaciones" element={<ObservacionesPage />} />

            {/* Revision Observaciones */}
            <Route path="/revision-observaciones" element={<RevisionObsPage />} />

            {/* Predicción */}
            <Route path="/prediccion" element={<PrediccionPage />} />

            {/* Reportes */}
            <Route path="/reportes" element={<ReportesPage />} />
          </Route>

          {/* Auth Layout */}
          <Route path="/signin" element={<SignIn />} />
          <Route path="/signup" element={<SignUp />} />

          {/* Fallback Route */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Router>
    </>
  );
}
