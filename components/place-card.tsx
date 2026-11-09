import Image from "next/image";
import type { Place } from "@/lib/places";

export function PlaceCard({ place }: { place: Place }) {
  return (
    <article className="group flex h-full flex-col overflow-hidden rounded-lg border border-border bg-card shadow-sm shadow-primary/5 transition-all hover:-translate-y-0.5 hover:border-secondary/60 hover:shadow-md hover:shadow-primary/10">
      <div className="relative aspect-[4/3] overflow-hidden bg-surface">
        <Image
          src={place.image}
          alt={place.name}
          fill
          sizes="(min-width: 1024px) 33vw, (min-width: 640px) 50vw, 100vw"
          className="object-cover transition-transform duration-500 group-hover:scale-105"
        />
        <span className="absolute left-3 top-3 rounded-full bg-background/90 px-3 py-1 text-xs font-semibold text-primary-strong backdrop-blur">
          {place.category}
        </span>
      </div>
      <div className="flex flex-1 flex-col p-5">
        <h3 className="font-serif text-xl font-semibold">{place.name}</h3>
        <p className="mt-1 flex items-center gap-2 text-sm font-medium text-primary">
          <span aria-hidden="true" className="h-1.5 w-1.5 rounded-full bg-accent" />
          {place.governorate}
        </p>
        <p className="mt-3 text-sm leading-relaxed text-muted">{place.description}</p>
      </div>
    </article>
  );
}

export function PlaceGrid({ places }: { places: Place[] }) {
  return (
    <ul className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {places.map((place) => (
        <li key={place.id}>
          <PlaceCard place={place} />
        </li>
      ))}
    </ul>
  );
}
