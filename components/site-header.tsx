import Link from "next/link";
import { MainNav } from "@/components/main-nav";

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-20 bg-background/95 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-4 sm:px-6">
        <Link href="/" className="font-serif text-2xl font-semibold text-primary">
          Kenooz
        </Link>
        <MainNav />
      </div>
      <div aria-hidden="true" className="sunset-gradient h-0.5 w-full opacity-80" />
    </header>
  );
}
