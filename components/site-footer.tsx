import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="bg-foreground text-background">
      <div aria-hidden="true" className="sunset-gradient h-1 w-full" />
      <div className="mx-auto flex max-w-6xl flex-col gap-4 px-6 py-6 text-sm text-background/80 sm:flex-row sm:items-center sm:justify-between">
        <p>&copy; {new Date().getFullYear()} Kenooz – Hidden Gems of Egypt</p>
        <nav aria-label="Footer">
          <ul className="flex gap-5">
            <li>
              <Link href="/" className="transition-colors hover:text-accent">
                Home
              </Link>
            </li>
            <li>
              <Link href="/explore" className="transition-colors hover:text-accent">
                Explore
              </Link>
            </li>
            <li>
              <Link href="/add-place" className="transition-colors hover:text-accent">
                Add a Place
              </Link>
            </li>
          </ul>
        </nav>
      </div>
    </footer>
  );
}
