import { Routes, Route, Navigate, Outlet } from 'react-router-dom'; // Import Outlet
import LoginPage from './pages/LoginPage';
import HomePage from './pages/HomePage';
import AITourPage from './pages/AITourPage';
import ToursListPage from './pages/ToursListPage';
import TourDetailPage from './pages/TourDetailPage';
import CreateTourPage from './pages/CreateTourPage';
import EditTourPage from './pages/EditTourPage'; // Import
import MainLayout from './components/layout/MainLayout';
import { useAuthStore } from './store/authStore';

function App() {
  const { token } = useAuthStore();

  // Component to handle protected routes with the main layout
  const ProtectedRoutesWithLayout = () => {
    if (!token) {
      return <Navigate to="/login" replace />;
    }
    return (
      <MainLayout>
        <Outlet /> {/* Child routes will render here */}
      </MainLayout>
    );
  };

  return (
    <Routes>
      <Route path="/login" element={!token ? <LoginPage /> : <Navigate to="/" />} />

      {/* Routes that use the MainLayout */}
      <Route element={<ProtectedRoutesWithLayout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/ai-tour-creation" element={<AITourPage />} />
        <Route path="/tours" element={<ToursListPage />} />
        <Route path="/tours/create" element={<CreateTourPage />} /> {/* New Route */}
        <Route path="/tours/:tourId" element={<TourDetailPage />} />
        {/* Add other protected routes here */}
      </Route>
      <Route path="*" element={<Navigate to={token ? "/" : "/login"} />} />
    </Routes>
  );
}

export default App;
