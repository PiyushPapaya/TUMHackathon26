import Link from "next/link";

type Variant = "primary" | "outline" | "outline-light" | "text";

const VARIANTS: Record<Variant, string> = {
  primary: "bg-[var(--blue)] text-white border border-[var(--blue)] hover:bg-[var(--blue-hover)] hover:border-[var(--blue-hover)]",
  outline: "bg-transparent text-[var(--ink)] border border-[var(--ink)] hover:bg-[var(--ink)] hover:text-white",
  "outline-light": "bg-transparent text-white border border-white hover:bg-white hover:text-[var(--black)]",
  text: "text-[var(--ink)] hover:text-[var(--blue)] border border-transparent px-0",
};

// Eckig, 52 px hoch (BMW-Knopfmaß). Ein Baustein statt kopierter Klassenketten.
export function buttonClass(variant: Variant = "primary", extra = "") {
  return `inline-flex h-[52px] items-center justify-center gap-2 px-7 text-[15px] font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-40 ${VARIANTS[variant]} ${extra}`;
}

type Props = {
  variant?: Variant;
  href?: string;
  external?: boolean;
  className?: string;
  children: React.ReactNode;
} & Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, "className">;

export function Button({ variant = "primary", href, external, className, children, ...rest }: Props) {
  const cls = buttonClass(variant, className);
  if (href && external) {
    return (
      <a className={cls} href={href} target="_blank" rel="noopener noreferrer">
        {children}
      </a>
    );
  }
  if (href) {
    return (
      <Link className={cls} href={href}>
        {children}
      </Link>
    );
  }
  return (
    <button type="button" className={cls} {...rest}>
      {children}
    </button>
  );
}
