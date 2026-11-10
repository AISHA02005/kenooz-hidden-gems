import type { Category, Place } from "@/lib/places";

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  details?: Record<string, string>;
}

export interface PlacesResponse {
  count: number;
  places: Place[];
}

export interface PlaceSubmitResponse {
  message: string;
  place: Place;
}

/**
 * Get the backend API base URL.
 * In server-side environments (SSR), resolves to the Flask API endpoint directly.
 * In browser environments, returns empty string so requests use same-origin Next.js rewrites.
 */
export function getApiBaseUrl(): string {
  if (typeof window === "undefined") {
    // Server-side execution
    return (
      process.env.API_BASE_URL ||
      process.env.NEXT_PUBLIC_API_URL ||
      "http://127.0.0.1:5000"
    );
  }
  // Client-side execution uses Next.js rewrites by default, or NEXT_PUBLIC_API_URL if configured
  return process.env.NEXT_PUBLIC_API_URL || "";
}

/**
 * Resolve the image source for a place.
 * Prefers image_url from API (/uploads/...), falls back to image, image_key, or placeholder.
 */
export function getPlaceImageUrl(place: Place): string {
  if (place.image_url) {
    return place.image_url;
  }
  if (place.image) {
    return place.image;
  }
  if (place.image_key) {
    return `/uploads/${place.image_key}`;
  }
  return "/places/siwa-shali.png";
}

/**
 * Fetch published places from the Flask API.
 * Never exposes pending places. Throws if the API request fails.
 */
export async function fetchPublishedPlaces(options?: {
  category?: string;
  governorate?: string;
  search?: string;
}): Promise<PlacesResponse> {
  const baseUrl = getApiBaseUrl();
  const url = new URL(`${baseUrl}/api/places`);

  if (options?.category && options.category.toLowerCase() !== "all") {
    url.searchParams.set("category", options.category);
  }
  if (options?.governorate && options.governorate.toLowerCase() !== "all") {
    url.searchParams.set("governorate", options.governorate);
  }
  if (options?.search) {
    url.searchParams.set("search", options.search.trim());
  }

  const res = await fetch(url.toString(), {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
    // Ensure fresh data on each request without stale static caching
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch places (HTTP ${res.status}): ${res.statusText}`);
  }

  const data: PlacesResponse = await res.json();
  return data;
}

/**
 * Submit a new place to the Flask API.
 * Accepts multipart/form-data. Browser automatically sets boundary.
 */
export async function submitPlace(formData: FormData): Promise<PlaceSubmitResponse> {
  const baseUrl = getApiBaseUrl();
  const res = await fetch(`${baseUrl}/api/places`, {
    method: "POST",
    body: formData,
    headers: {
      Accept: "application/json",
    },
  });

  const data = await res.json();

  if (!res.ok) {
    const error = new Error(data.error || "Failed to submit place") as Error & {
      details?: Record<string, string>;
      status?: number;
    };
    error.details = data.details;
    error.status = res.status;
    throw error;
  }

  return data as PlaceSubmitResponse;
}
