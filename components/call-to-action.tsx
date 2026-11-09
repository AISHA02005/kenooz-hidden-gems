import { ButtonLink } from "@/components/ui";

export function CallToAction() {
  return (
    <section className="px-6 pb-16 md:pb-24">
      <div className="mx-auto max-w-6xl overflow-hidden rounded-xl bg-foreground text-background">
        <div aria-hidden="true" className="sunset-gradient h-1 w-full" />
        <div className="flex flex-col items-start gap-6 p-8 md:flex-row md:items-center md:justify-between md:p-12">
          <div className="max-w-xl">
            <h2 className="text-balance font-serif text-3xl font-semibold md:text-4xl">
              Egypt has more stories to tell
            </h2>
            <p className="mt-3 leading-relaxed text-background/80">
              Start exploring hidden gems across every governorate, or share a place you love so
              others can discover it too.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <ButtonLink href="/explore" className="bg-accent text-foreground hover:bg-secondary">
              Explore Egypt
            </ButtonLink>
            <ButtonLink
              href="/add-place"
              variant="secondary"
              className="border-background/30 bg-transparent text-background hover:border-accent hover:bg-background/10"
            >
              Add a place
            </ButtonLink>
          </div>
        </div>
      </div>
    </section>
  );
}
