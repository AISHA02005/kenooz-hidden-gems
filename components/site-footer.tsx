export function SiteFooter() {
  return (
    <footer className="bg-foreground text-background">
      <div aria-hidden="true" className="sunset-gradient h-1 w-full" />
      <div className="mx-auto max-w-6xl px-6 py-6 text-sm text-background/80">
        &copy; {new Date().getFullYear()} Kenooz – Hidden Gems of Egypt
      </div>
    </footer>
  );
}
