export function Hero() {
  return (
    <section id="about" className="sunset-glow">
      <div className="mx-auto max-w-6xl px-6 py-20 md:py-32">
      <p className="flex items-center gap-3 text-sm font-semibold uppercase tracking-widest text-primary-strong">
        <span aria-hidden="true" className="h-px w-8 bg-accent" />Discover authentic Egypt</p>
      <h1 className="mt-4 max-w-3xl text-balance font-serif text-4xl font-semibold leading-tight md:text-6xl">
        Kenooz – Hidden Gems of Egypt
      </h1>
      <p className="mt-6 max-w-2xl text-pretty text-lg leading-relaxed text-muted">
        Kenooz is a platform for discovering Egypt beyond the pyramids. Explore quiet oases,
        forgotten temples, local artisans, and authentic experiences shared by travelers and
        locals who know the country best.
      </p>
      <div className="mt-10 flex flex-wrap gap-4">
        <a
          href="#explore"
          className="rounded-md bg-primary-strong px-6 py-3 text-sm font-semibold text-primary-foreground shadow-sm shadow-primary/20 transition-colors hover:bg-primary focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
        >
          Start exploring
        </a>
        <a
          href="#explore"
          className="rounded-md border border-primary/30 bg-card/60 px-6 py-3 text-sm font-semibold text-foreground transition-colors hover:border-secondary hover:bg-secondary/10 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
        >
          Learn more
        </a>
      </div>
      </div>
    </section>
  );
}
