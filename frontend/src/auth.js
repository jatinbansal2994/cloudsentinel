import {
  CognitoUserPool,
  CognitoUser,
  AuthenticationDetails,
} from "amazon-cognito-identity-js";

const poolData = {
  UserPoolId: import.meta.env.VITE_USER_POOL_ID,
  ClientId: import.meta.env.VITE_USER_POOL_CLIENT_ID,
};

const userPool = new CognitoUserPool(poolData);

export function login(username, password) {
  return new Promise((resolve, reject) => {
    const user = new CognitoUser({ Username: username, Pool: userPool });
    const authDetails = new AuthenticationDetails({ Username: username, Password: password });
    user.authenticateUser(authDetails, {
      onSuccess: (session) => resolve(session),
      onFailure: (err) => reject(err),
    });
  });
}

export function logout() {
  const user = userPool.getCurrentUser();
  if (user) user.signOut();
}

export function getSession() {
  return new Promise((resolve, reject) => {
    const user = userPool.getCurrentUser();
    if (!user) return reject(new Error("No user"));
    user.getSession((err, session) => {
      if (err || !session.isValid()) return reject(err || new Error("Invalid session"));
      resolve(session);
    });
  });
}

export async function getIdToken() {
  const session = await getSession();
  return session.getIdToken().getJwtToken();
}
