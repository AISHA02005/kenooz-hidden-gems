import type { Metadata } from "next";
import { SiteShell } from "@/components/site-shell";
import { PageHeader } from "@/components/ui";
import { AddPlaceForm } from "@/components/add-place-form";

export const metadata: Metadata = {
  title: "Add a Place – Kenooz",
  description: "Share a hidden gem in Egypt with the Kenooz community.",
};

export default function AddPlacePage() {
  return (
    <SiteShell>
      <PageHeader
        eyebrow="Share a gem"
        title="Add a place"
        description="Know a spot most travelers miss? Tell us about it so others can discover it too."
      />
      <section className="mx-auto max-w-3xl px-6 py-12 md:py-16">
        <AddPlaceForm />
      </section>
    </SiteShell>
  );
}
