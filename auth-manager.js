import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.4/firebase-app.js";
import { getAuth, onAuthStateChanged, signInWithEmailAndPassword, createUserWithEmailAndPassword, signOut, updateProfile } from "https://www.gstatic.com/firebasejs/10.12.4/firebase-auth.js";

const firebaseConfig = {
    apiKey: "AIzaSyCtG3X-ycPgIT17sk99tkCjxOsHc4jv4Ls",
    authDomain: "go-vista.firebaseapp.com",
    projectId: "go-vista",
    storageBucket: "go-vista.appspot.com",
    messagingSenderId: "177827888478",
    appId: "1:177827888478:web:b167551b290548f56423cf"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

/**
 * Ensures user is authenticated. Redirects to auth.html if not.
 */
export function checkAuth(redirectIfNotAuth = true) {
    return new Promise((resolve) => {
        onAuthStateChanged(auth, (user) => {
            if (user) {
                resolve(user);
            } else {
                if (redirectIfNotAuth && !window.location.pathname.includes('auth.html')) {
                    window.location.href = 'auth.html';
                }
                resolve(null);
            }
        });
    });
}

export async function login(email, password) {
    try {
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        return userCredential.user;
    } catch (error) {
        throw error;
    }
}

export async function signup(name, email, password) {
    try {
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        await updateProfile(userCredential.user, { displayName: name });
        return userCredential.user;
    } catch (error) {
        throw error;
    }
}

export async function logout() {
    try {
        await signOut(auth);
        window.location.href = 'auth.html';
    } catch (error) {
        console.error("Logout Error:", error);
    }
}

export { auth };
