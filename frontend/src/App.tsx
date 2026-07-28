import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Dashboard } from './views/Dashboard/Dashboard';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { SettingView } from './views/SettingsView/SettingView';
import { NotFound } from './views/NotFound';

export default function App() {
  const queryClient = new QueryClient();

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="*" element={<NotFound />} />
          <Route path="/" element={<Dashboard />} />
          <Route path="/settings" element={<SettingView />} />
        </Routes>  
      </BrowserRouter>
    </QueryClientProvider>
  )
}