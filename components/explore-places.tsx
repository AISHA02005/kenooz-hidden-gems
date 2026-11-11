"use client";

import { useMemo, useState } from "react";
import { PlaceGrid } from "@/components/place-card";
import { fieldStyles } from "@/components/ui";
import { CATEGORIES, type Place } from "@/lib/places";
import { fetchPublishedPlaces } from "@/lib/api";

const ALL = "all";

interface ExplorePlacesProps {
  initialPlaces?: Place[];
  initialError?: string | null;
}

export function ExplorePlaces({
  initialPlaces = [],
  initialError = null,
}: ExplorePlacesProps) {
  const [retryPlaces, setRetryPlaces] = useState<Place[] | null>(null);
  const [error, setError] = useState<string | null>(initialError);
  const [isLoading, setIsLoading] = useState(false);

  const places = retryPlaces ?? initialPlaces;

  const [query, setQuery] = useState("");
  const [category, setCategory] = useState(ALL);
  const [governorate, setGovernorate] = useState(ALL);

  const governoratesWithPlaces = useMemo(() => {
    return Array.from(new Set(places.map((p) => p.governorate))).sort();
  }, [places]);

  const results = useMemo(() => {
    const q = query.trim().toLowerCase();

    return places.filter((place) => {
      const nameMatch = !q || place.name.toLowerCase().includes(q);
      const catMatch = category === ALL || place.category === category;
      const govMatch = governorate === ALL || place.governorate === governorate;

      return nameMatch && catMatch && govMatch;
    });
  }, [places, query, category, governorate]);

  const hasFilters = query !== "" || category !== ALL || governorate !== ALL;

  function resetFilters() {
    setQuery("");
    setCategory(ALL);
    setGovernorate(ALL);
  }

  async function handleRetry() {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchPublishedPlaces();
      setRetryPlaces(data.places);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load places from the API service.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="mx-auto max-w-6xl px-6 py-12 md:py-16">
      {error && (
        <div className="mb-8 rounded-lg border border-border bg-card p-6 shadow-sm">
          <p className="font-serif text-xl font-semibold text-primary-strong">
            Unable to load places from the backend
          </p>
          <p className="mt-2 text-sm text-muted">{error}</p>
          <button
            type="button"
            onClick={handleRetry}
            disabled={isLoading}
            className="mt-4 text-sm font-semibold text-primary-strong underline-offset-4 hover:underline disabled:opacity-50"
          >
            {isLoading ? "Retrying..." : "Try again"}
          </button>
        </div>
      )}

      <form
        role="search"
        onSubmit={(e) => e.preventDefault()}
        className="grid gap-4 rounded-lg border border-border bg-surface p-4 md:grid-cols-[2fr_1fr_1fr] md:p-5"
      >
        <div className="flex flex-col gap-1.5">
          <label htmlFor="search" className="text-sm font-medium">
            Search by name
          </label>
          <input
            id="search"
            type="search"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
            }}
            placeholder="e.g. White Desert"
            className={fieldStyles}
          />
        </div>
        <div className="flex flex-col gap-1.5">
          <label htmlFor="category" className="text-sm font-medium">
            Category
          </label>
          <select
            id="category"
            value={category}
            onChange={(e) => {
              setCategory(e.target.value);
            }}
            className={fieldStyles}
          >
            <option value={ALL}>All categories</option>
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
        <div className="flex flex-col gap-1.5">
          <label htmlFor="governorate" className="text-sm font-medium">
            Governorate
          </label>
          <select
            id="governorate"
            value={governorate}
            onChange={(e) => {
              setGovernorate(e.target.value);
            }}
            className={fieldStyles}
          >
            <option value={ALL}>All governorates</option>
            {governoratesWithPlaces.map((g) => (
              <option key={g} value={g}>
                {g}
              </option>
            ))}
          </select>
        </div>
      </form>

      <div className="mt-8 flex items-center justify-between gap-4">
        <p className="text-sm text-muted" aria-live="polite">
          Showing {results.length} of {places.length} places
        </p>
        {hasFilters && (
          <button
            type="button"
            onClick={resetFilters}
            className="text-sm font-semibold text-primary-strong underline-offset-4 hover:underline"
          >
            Clear filters
          </button>
        )}
      </div>

      <div className="mt-6">
        {results.length > 0 ? (
          <PlaceGrid places={results} />
        ) : (
          <div className="rounded-lg border border-dashed border-border bg-card px-6 py-16 text-center">
            <h2 className="font-serif text-2xl font-semibold">No places found</h2>
            <p className="mt-2 text-muted">
              {places.length === 0
                ? "No published places are available at the moment."
                : "Try a different name or adjust the filters."}
            </p>
          </div>
        )}
      </div>
    </section>
  );
}