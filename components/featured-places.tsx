import Link from "next/link";
import { PlaceGrid } from "@/components/place-card";
import type { Place } from "@/lib/places";

interface FeaturedPlacesProps {
  places?: Place[];
  error?: string | null;
}

export function FeaturedPlaces({ places = [], error = null }: FeaturedPlacesProps) {
  return (
    <section className="mx-auto max-w-6xl px-6 py-16 md:py-24">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 className="font-serif text-3xl font-semibold md:text-4xl">Featured places</h2>
          <p className="mt-3 max-w-xl leading-relaxed text-muted">
            A few favorites from the Kenooz community, from desert fortresses to Nile-side villages.
          </p>
        </div>
        <Link
          href="/explore"
          className="text-sm font-semibold text-primary-strong underline-offset-4 hover:underline"
        >
          View all places
        </Link>
      </div>

      <div className="mt-10">
        {error ? (
          <div className="rounded-lg border border-dashed border-border bg-card p-8 text-center shadow-sm">
            <p className="font-serif text-xl font-semibold text-primary-strong">
              Unable to load featured places
            </p>
            <p className="mt-2 text-sm text-muted">{error}</p>
          </div>
        ) : places.length > 0 ? (
          <PlaceGrid places={places} />
        ) : (
          <div className="rounded-lg border border-dashed border-border bg-card p-8 text-center">
            <p className="text-muted">No featured places available at the moment.</p>
          </div>
        )}
      </div>
    </section>
  );
}
