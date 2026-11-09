import type { Metadata } from "next";
import { SiteShell } from "@/components/site-shell";
import { PageHeader } from "@/components/ui";
import { ExplorePlaces } from "@/components/explore-places";

export const metadata: Metadata = {
  title: "Explore – Kenooz",
  description: "Search and filter hidden gems across Egypt by category and governorate.",
};

export default function ExplorePage() {
  return (
    <SiteShell>
      <PageHeader
        eyebrow="Explore"
        title="Find your next hidden gem"
        description="Browse places shared by travelers and locals. Search by name or filter by category and governorate to find something new."
      />
      <ExplorePlaces />
    </SiteShell>
  );
}
