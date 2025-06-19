import { initializeApp, getApps, getApp } from "firebase/app";
import { getAuth } from "firebase/auth";

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

// --- Inicialización de la App ---
// Si ya hay una app de Firebase inicializada, la usamos; si no, la creamos.
// Esto previene errores durante el Hot Reload en desarrollo.
const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();

// --- Exportación de Servicios ---
// Exportamos la instancia de autenticación para usarla en otras partes de la app.
export const auth = getAuth(app); 