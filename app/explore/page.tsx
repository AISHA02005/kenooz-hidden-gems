import type { Metadata } from "next";
import { SiteShell } from "@/components/site-shell";
import { PageHeader } from "@/components/ui";
import { ExplorePlaces } from "@/components/explore-places";
import { fetchPublishedPlaces } from "@/lib/api";
import type { Place } from "@/lib/places";

export const metadata: Metadata = {
  title: "Explore – Kenooz",
  description: "Search and filter hidden gems across Egypt by category and governorate.",
};

export default async function ExplorePage() {
  let places: Place[] = [];
  let error: string | null = null;

  try {
    const data = await fetchPublishedPlaces();
    places = data.places;
  } catch (err) {
    error =
      err instanceof Error
        ? err.message
        : "Failed to connect to the Kenooz API service.";
  }

  return (
    <SiteShell>
      <PageHeader
        eyebrow="Explore"
        title="Find your next hidden gem"
        description="Browse places shared by travelers and locals. Search by name or filter by category and governorate to find something new."
      />
      <ExplorePlaces initialPlaces={places} initialError={error} />
    </SiteShell>
  );
}
