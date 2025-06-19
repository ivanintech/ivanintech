import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Convierte una URL de un blob de GitHub a su URL "raw" para acceso directo al fichero.
 * @param url La URL de GitHub a convertir.
 * @returns La URL "raw" si es una URL de GitHub válida, si no, devuelve la URL original.
 */
export function convertToRawGitHubUrl(url: string | null | undefined): string {
  if (!url) return "";
  
  if (url.includes("github.com") && url.includes("/blob/")) {
    return url
      .replace("github.com", "raw.githubusercontent.com")
      .replace("/blob/", "/");
  }
  
  return url;
}
