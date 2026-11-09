export function Hero() {
  return (
    <section id="about" className="mx-auto max-w-6xl px-6 py-20 md:py-32">
      <p className="text-sm font-medium uppercase tracking-widest text-accent">Discover authentic Egypt</p>
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
          className="rounded-md bg-primary px-6 py-3 text-sm font-medium text-primary-foreground hover:opacity-90"
        >
          Start exploring
        </a>
        <a
          href="#explore"
          className="rounded-md border border-border px-6 py-3 text-sm font-medium hover:bg-card"
        >
          Learn more
        </a>
      </div>
    </section>
  );
}
