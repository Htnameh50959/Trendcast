import React, { useEffect, useState } from "react";
import "./app.css";
import { Sidebar } from "./ui/sidebar";
import { Route, Switch, useLocation } from "wouter";
import Salesdata from "./page/salesdata";
import Dashboard from "./page/Dashboard";
import { ToastContainer } from "./ui/toast";
import Forecasts from "./page/forecasts";
import AuthModal from "./page/AuthModal";
import { AuthProvider, useAuth } from "./page/AuthModal";

function Router() {
  const [location, setLocation] = useLocation();
  const { isAuthenticated, loading } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);

  useEffect(() => {
    // Redirect authenticated users away from auth modal
    if (isAuthenticated && location === "/") {
      // Allow staying on the same page
    }
  }, [location, isAuthenticated]);

  if (loading && false) {
    return <div className="loading-container">Loading...</div>;
  }

  return (
    <>
      <Switch>
        <Route path="/">
          <div className="flex h-screen overflow-hidden bg-[#f8f9fc]">
            <Sidebar onLoginClick={() => setShowAuthModal(true)} />
            <main className="flex-1 overflow-y-auto">
              <Dashboard />
            </main>
            <ToastContainer />
          </div>
        </Route>
        <Route path="/Sales">
          <div className="flex h-screen overflow-hidden bg-[#f8f9fc]">
            <Sidebar onLoginClick={() => setShowAuthModal(true)} />
            <main className="flex-1 overflow-y-auto p-6">
              <div className="max-w-6xl mx-auto">
                <Salesdata />
              </div>
            </main>
            <ToastContainer />
          </div>
        </Route>
        <Route path="/Forecasts">
          <div className="flex h-screen overflow-hidden bg-[#f8f9fc]">
            <Sidebar onLoginClick={() => setShowAuthModal(true)} />
            <main className="flex-1 overflow-y-auto p-6">
              <div className="max-w-6xl mx-auto">
                <Forecasts />
              </div>
            </main>
            <ToastContainer />
          </div>
        </Route>
      </Switch>

      <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} />
    </>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router />
    </AuthProvider>
  );
}

export default App;