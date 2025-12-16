import React from 'react';
import ReactDOM from 'react-dom/client';
import { HashRouter } from 'react-router-dom';
import App from './App';

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error("Could not find root element to mount to");
}

const root = ReactDOM.createRoot(rootElement);

try {
  root.render(
    <React.StrictMode>
      <HashRouter>
        <App />
      </HashRouter>
    </React.StrictMode>
  );
} catch (error) {
  console.error("Application render error:", error);
  rootElement.innerHTML = '<div style="padding: 20px; text-align: center;"><h1>Bir hata oluştu</h1><p>Sayfayı yenilemeyi deneyin.</p></div>';
}