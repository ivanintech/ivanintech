import { initializeApp, getApps, getApp, type FirebaseApp } from "firebase/app";
import { getAuth, type Auth } from "firebase/auth";

// --- Configuración de Firebase ---
// Las variables de entorno deben estar en .env.local y en Render/Vercel
const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};

let app: FirebaseApp | null = null;
let auth: Auth | null = null;

// Solo inicializamos Firebase si la API key está presente.
if (firebaseConfig.apiKey) {
  app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
  auth = getAuth(app);
} else {
  // Si estamos en el navegador, mostramos una advertencia clara.
  if (typeof window !== 'undefined') {
    console.warn(
      "ADVERTENCIA: Clave de API de Firebase no encontrada. La autenticación estará deshabilitada. " +
      "Asegúrate de que las variables de entorno NEXT_PUBLIC_FIREBASE_* están configuradas en tu fichero .env.local"
    );
  }
}

// Exportamos 'auth', que será null si no hay configuración.
export { auth }; 