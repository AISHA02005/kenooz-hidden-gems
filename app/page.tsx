import { SiteShell } from "@/components/site-shell";
import { Hero } from "@/components/hero";
import { Features } from "@/components/features";
import { FeaturedPlaces } from "@/components/featured-places";
import { CallToAction } from "@/components/call-to-action";
import { fetchPublishedPlaces } from "@/lib/api";
import type { Place } from "@/lib/places";

export default async function HomePage() {
  let places: Place[] = [];
  let error: string | null = null;

  try {
    const response = await fetchPublishedPlaces();
    places = response.places.slice(0, 6);
  } catch (err) {
    error =
      err instanceof Error
        ? err.message
        : "Failed to connect to the Kenooz API service.";
  }

  return (
    <SiteShell>
      <Hero />
      <Features />
      <FeaturedPlaces places={places} error={error} />
      <CallToAction />
    </SiteShell>
  );
}
