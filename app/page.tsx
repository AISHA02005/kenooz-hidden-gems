import { SiteShell } from "@/components/site-shell";
import { Hero } from "@/components/hero";
import { Features } from "@/components/features";
import { FeaturedPlaces } from "@/components/featured-places";
import { CallToAction } from "@/components/call-to-action";

export default function HomePage() {
  return (
    <SiteShell>
      <Hero />
      <Features />
      <FeaturedPlaces />
      <CallToAction />
    </SiteShell>
  );
}
