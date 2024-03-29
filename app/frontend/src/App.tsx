import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./components/Login";
import SignUp from "./components/SignUp";
import Profile from "./components/Profile";
import { AuthProvider } from "./AuthContext";

export const StatusMessageContext = React.createContext({
  setStatusMessage: (message: string) => {
    console.log(message);
  },
});

const App = () => {
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
  const [username, setUsername] = useState<string>("");
  const [statusMessage, setStatusMessage] = useState<string>("");

  const checkLoginStatus = async () => {
    const response = await fetch("/api/status");
    const data = await response.json();
    setIsLoggedIn(data.logged_in);
    setUsername(data.username);
  };

  useEffect(() => {
    checkLoginStatus();
  }, [statusMessage]);

  return (
    <AuthProvider>
      <StatusMessageContext.Provider value={{ setStatusMessage }}>
        <nav>
          <h1>Welcome</h1>
          {statusMessage && <p>{statusMessage}</p>}
          {isLoggedIn ? (
            <>
              <span>logged in as {username}. </span>
              <a href="/api/logout">Logout</a>
            </>
          ) : (
            "not logged in"
          )}
        </nav>
        <BrowserRouter>
          <Routes>
            <Route
              path="/"
              element={isLoggedIn ? <Navigate to="/profile" /> : <Login />}
            />
            <Route path="/signup" element={<SignUp />} />
            <Route
              path="/profile"
              element={isLoggedIn ? <Profile /> : <Navigate to="/" />}
            />
          </Routes>
        </BrowserRouter>
      </StatusMessageContext.Provider>
    </AuthProvider>
  );
};

export default App;
