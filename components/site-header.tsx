import Link from "next/link";

export function SiteHeader() {
  return (
    <header className="relative bg-background">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link href="/" className="font-serif text-2xl font-semibold text-primary">
          Kenooz
        </Link>
        <nav aria-label="Main">
          <ul className="flex items-center gap-6 text-sm font-medium text-muted">
            <li>
              <a href="#about" className="transition-colors hover:text-primary-strong">
                About
              </a>
            </li>
            <li>
              <a href="#explore" className="transition-colors hover:text-primary-strong">
                Explore
              </a>
            </li>
          </ul>
        </nav>
      </div>
      <div aria-hidden="true" className="sunset-gradient h-0.5 w-full opacity-80" />
    </header>
  );
}
