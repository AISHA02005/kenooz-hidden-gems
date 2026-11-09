import Link from "next/link";

export function SiteHeader() {
  return (
    <header className="border-b border-border">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link href="/" className="font-serif text-2xl font-semibold text-primary">
          Kenooz
        </Link>
        <nav aria-label="Main">
          <ul className="flex items-center gap-6 text-sm text-muted">
            <li>
              <a href="#about" className="hover:text-foreground">
                About
              </a>
            </li>
            <li>
              <a href="#explore" className="hover:text-foreground">
                Explore
              </a>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
}
