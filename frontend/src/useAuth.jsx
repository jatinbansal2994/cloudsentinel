import { useState, useEffect, createContext, useContext } from "react";
import { getSession, login as cognitoLogin, logout as cognitoLogout } from "./auth";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(undefined); // undefined = loading

  useEffect(() => {
    getSession()
      .then((s) => setUser(s.getIdToken().payload))
      .catch(() => setUser(null));
  }, []);

  async function login(username, password) {
    const session = await cognitoLogin(username, password);
    setUser(session.getIdToken().payload);
  }

  function logout() {
    cognitoLogout();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
