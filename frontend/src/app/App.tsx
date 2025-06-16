import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { AppRouter } from './router';

function App() {
  return (
    <BrowserRouter>
      {/* В будущем здесь будет компонент MainLayout */}
      <AppRouter />
    </BrowserRouter>
  );
}

export default App;