import { ICONS } from "./icons";

export type IconName = keyof typeof ICONS;

/** Ícono de línea de GOLIAT. Hereda el color del texto (currentColor). Decorativo salvo que se pase `label`. */
export function Icon({ name, size = 22, label, className }: { name: IconName; size?: number; label?: string; className?: string }) {
  return (
    <svg
      className={className}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      strokeLinecap="round"
      strokeLinejoin="round"
      role={label ? "img" : undefined}
      aria-label={label}
      aria-hidden={label ? undefined : true}
      dangerouslySetInnerHTML={{ __html: ICONS[name] }}
    />
  );
}
