const features = [
  {
    title: "Discover places",
    description: "Find lesser-known sites, from Siwa's salt lakes to the painted tombs of Middle Egypt.",
  },
  {
    title: "Share your finds",
    description: "Add hidden gems you've visited with photos and tips to help fellow travelers.",
  },
  {
    title: "Support local",
    description: "Connect with local guides, artisans, and family-run guesthouses across Egypt.",
  },
];

export function Features() {
  return (
    <section id="explore" className="border-t border-border bg-gradient-to-b from-surface to-background">
      <div className="mx-auto max-w-6xl px-6 py-16 md:py-24">
        <h2 className="font-serif text-3xl font-semibold">What you can do with Kenooz</h2>
        <ul className="mt-10 grid gap-6 md:grid-cols-3">
          {features.map((feature) => (
            <li
              key={feature.title}
              className="relative overflow-hidden rounded-lg border border-border bg-card p-6 shadow-sm shadow-primary/5 transition-colors before:absolute before:inset-x-0 before:top-0 before:h-1 before:bg-[linear-gradient(90deg,var(--primary),var(--secondary),var(--accent))] hover:border-secondary/60"
            >
              <h3 className="font-serif text-xl font-semibold text-primary">{feature.title}</h3>
              <p className="mt-3 leading-relaxed text-muted">{feature.description}</p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
