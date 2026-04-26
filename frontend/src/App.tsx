import { Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import Home from "./pages/Home";
import Tariffs from "./pages/Tariffs";
import Connect from "./pages/Connect";
import Referral from "./pages/Referral";
import Help from "./pages/Help";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/tariffs" element={<Tariffs />} />
        <Route path="/connect" element={<Connect />} />
        <Route path="/referral" element={<Referral />} />
        <Route path="/help" element={<Help />} />
      </Route>
    </Routes>
  );
}
