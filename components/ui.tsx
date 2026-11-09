import Link from "next/link";
import type { ComponentProps } from "react";

const buttonBase =
  "inline-flex items-center justify-center rounded-md px-6 py-3 text-sm font-semibold transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:cursor-not-allowed disabled:opacity-60";

export const buttonStyles = {
  primary: `${buttonBase} bg-primary-strong text-primary-foreground shadow-sm shadow-primary/20 hover:bg-primary`,
  secondary: `${buttonBase} border border-primary/30 bg-card/60 text-foreground hover:border-secondary hover:bg-secondary/10`,
};

export function ButtonLink({
  variant = "primary",
  className = "",
  ...props
}: ComponentProps<typeof Link> & { variant?: keyof typeof buttonStyles }) {
  return <Link className={`${buttonStyles[variant]} ${className}`} {...props} />;
}

export const fieldStyles =
  "w-full rounded-md border border-border bg-card px-4 py-2.5 text-sm text-foreground placeholder:text-muted/70 transition-colors focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 aria-[invalid=true]:border-primary-strong";

export function PageHeader({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string;
  title: string;
  description: string;
}) {
  return (
    <section className="sunset-glow border-b border-border">
      <div className="mx-auto max-w-6xl px-6 py-14 md:py-20">
        <p className="flex items-center gap-3 text-sm font-semibold uppercase tracking-widest text-primary-strong">
          <span aria-hidden="true" className="h-px w-8 bg-accent" />
          {eyebrow}
        </p>
        <h1 className="mt-4 max-w-3xl text-balance font-serif text-4xl font-semibold leading-tight md:text-5xl">
          {title}
        </h1>
        <p className="mt-4 max-w-2xl text-pretty text-lg leading-relaxed text-muted">{description}</p>
      </div>
    </section>
  );
}
