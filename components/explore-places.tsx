"use client";

import { useMemo, useState } from "react";
import { PlaceGrid } from "@/components/place-card";
import { fieldStyles } from "@/components/ui";
import { CATEGORIES, PLACES } from "@/lib/places";

const ALL = "all";
const governoratesWithPlaces = Array.from(new Set(PLACES.map((p) => p.governorate))).sort();

export function ExplorePlaces() {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState(ALL);
  const [governorate, setGovernorate] = useState(ALL);

  const results = useMemo(() => {
    const q = query.trim().toLowerCase();
    return PLACES.filter(
      (place) =>
        (!q || place.name.toLowerCase().includes(q)) &&
        (category === ALL || place.category === category) &&
        (governorate === ALL || place.governorate === governorate),
    );
  }, [query, category, governorate]);

  const hasFilters = query !== "" || category !== ALL || governorate !== ALL;

  function resetFilters() {
    setQuery("");
    setCategory(ALL);
    setGovernorate(ALL);
  }

  return (
    <section className="mx-auto max-w-6xl px-6 py-12 md:py-16">
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
            onChange={(e) => setQuery(e.target.value)}
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
            onChange={(e) => setCategory(e.target.value)}
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
            onChange={(e) => setGovernorate(e.target.value)}
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
          Showing {results.length} of {PLACES.length} places
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
            <p className="mt-2 text-muted">Try a different name or adjust the filters.</p>
          </div>
        )}
      </div>
    </section>
  );
}
