import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AppointmentsView } from './views/AppointmentsView/AppointmentsView';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { SettingView } from './views/SettingsView/SettingView';
import { NotFound } from './views/NotFound';
import { LoginView } from './views/AuthView/LoginView';

export default function App() {
  const queryClient = new QueryClient();

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="*" element={<NotFound />} />
          <Route path="/" element={<AppointmentsView />} />
          <Route path="/login" element={<LoginView />} />
          <Route path="/settings" element={<SettingView />} />
        </Routes>  
      </BrowserRouter>
    </QueryClientProvider>
  )
}