import { onAuthStateChange, getIdToken } from './firebase';
import { getUser, createUser, getUserByEmail } from './users';

const STORAGE_KEY = 'currentUser';
const PROFILE_KEY = 'userProfile';
let listeners = [];
let currentUser = null;
let userProfile = null;

let unsubscribe = null;

const initializeAuthListener = () => {
  if (unsubscribe) return;

  unsubscribe = onAuthStateChange(async (firebaseUser) => {
    if (firebaseUser) {
      try {
        let backendUser = null;

        try {
          backendUser = await getUserByEmail(firebaseUser.email);
        } catch (error) {
          console.log('User not found in backend, creating...');
          try {
            backendUser = await createUser({
              name: firebaseUser.displayName || firebaseUser.email.split('@')[0],
              email: firebaseUser.email,
              username: firebaseUser.email.split('@')[0],
              firebase_uid: firebaseUser.uid
            });
          } catch (createError) {
            console.error('Error creating user in backend:', createError);
          }
        }

        if (backendUser && backendUser.firebase_uid) {
          const fullProfile = await getUser(backendUser.firebase_uid);
          userProfile = fullProfile;
          localStorage.setItem(PROFILE_KEY, JSON.stringify(fullProfile));

          const combinedUser = {
            ...fullProfile,
            firebaseUid: firebaseUser.uid,
            displayName: firebaseUser.displayName,
            emailVerified: firebaseUser.emailVerified
          };

          currentUser = combinedUser;
          localStorage.setItem(STORAGE_KEY, JSON.stringify(combinedUser));

          listeners.forEach((cb) => {
            try { cb(combinedUser); } catch (e) {}
          });
        } else {
          const firebaseOnlyUser = {
            id: null,
            name: firebaseUser.displayName || firebaseUser.email.split('@')[0],
            email: firebaseUser.email,
            firebaseUid: firebaseUser.uid,
            displayName: firebaseUser.displayName,
            emailVerified: firebaseUser.emailVerified
          };

          currentUser = firebaseOnlyUser;
          localStorage.setItem(STORAGE_KEY, JSON.stringify(firebaseOnlyUser));

          listeners.forEach((cb) => {
            try { cb(firebaseOnlyUser); } catch (e) {}
          });
        }
      } catch (error) {
        console.error('Error syncing user with backend:', error);
        const firebaseOnlyUser = {
          id: null,
          name: firebaseUser.displayName || firebaseUser.email.split('@')[0],
          email: firebaseUser.email,
          firebaseUid: firebaseUser.uid,
          displayName: firebaseUser.displayName,
          emailVerified: firebaseUser.emailVerified
        };

        currentUser = firebaseOnlyUser;
        localStorage.setItem(STORAGE_KEY, JSON.stringify(firebaseOnlyUser));

        listeners.forEach((cb) => {
          try { cb(firebaseOnlyUser); } catch (e) {}
        });
      }
    } else {
      currentUser = null;
      userProfile = null;
      localStorage.removeItem(STORAGE_KEY);
      localStorage.removeItem(PROFILE_KEY);

      listeners.forEach((cb) => {
        try { cb(null); } catch (e) {}
      });
    }
  });
};

initializeAuthListener();

export function getCurrentUser() {
  if (currentUser) return currentUser;

  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const storedUser = raw ? JSON.parse(raw) : null;
    currentUser = storedUser;

    if (!userProfile) {
      const profileRaw = localStorage.getItem(PROFILE_KEY);
      if (profileRaw) {
        userProfile = JSON.parse(profileRaw);
      }
    }

    return storedUser;
  } catch (e) {
    return null;
  }
}

export function getUserProfile() {
  return userProfile;
}

function setCurrentUser(user) {
  try {
    currentUser = user;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
    listeners.forEach((cb) => {
      try { cb(user); } catch (e) {}
    });
  } catch (e) {
  }
}

function clearCurrentUser() {
  try {
    currentUser = null;
    userProfile = null;
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(PROFILE_KEY);
    listeners.forEach((cb) => {
      try { cb(null); } catch (e) {}
    });
  } catch (e) {
  }
}

export function onUserChange(callback) {
  listeners.push(callback);
  return () => {
    listeners = listeners.filter((cb) => cb !== callback);
  };
}

export async function getCurrentUserToken() {
  try {
    const token = await getIdToken();
    if (token) {
      return token;
    }

    for (let i = 0; i < 4; i++) {
      await new Promise(resolve => setTimeout(resolve, 500));
      const retryToken = await getIdToken();
      if (retryToken) {
        return retryToken;
      }
    }

    console.warn('Unable to get Firebase token after retries');
    return null;
  } catch (error) {
    console.error('Error getting user token:', error);
    return null;
  }
}
