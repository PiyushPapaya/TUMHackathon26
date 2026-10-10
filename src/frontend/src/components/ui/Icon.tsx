// Selbst gezeichnete Linien-Icons (1.5 px Strich, eckige Enden), keine Fremd-Assets.
// Warum eigene SVGs: BMW-Look braucht dünne Linien, und es gibt keine neue Abhängigkeit.
const PATHS = {
  list: "M4 6h16M4 12h16M4 18h10",
  evidence: "M5 4h10l4 4v12H5zM15 4v4h4M8 13h8M8 17h5",
  sliders: "M4 7h10M18 7h2M4 17h2M10 17h10M14 4v6M6 14v6",
  audit: "M12 3l8 3v6c0 4.5-3.2 7.8-8 9-4.8-1.2-8-4.5-8-9V6zM8.5 12l2.5 2.5L16 9.5",
  arrow: "M5 12h14M13 6l6 6-6 6",
  chevron: "M9 5l7 7-7 7",
  down: "M5 9l7 7 7-7",
  menu: "M4 8h16M4 16h16",
  close: "M6 6l12 12M18 6L6 18",
  chat: "M4 5h16v11H9l-5 4z",
  download: "M12 4v11M7 11l5 5 5-5M5 20h14",
  up: "M12 19V5M6 11l6-6 6 6",
} as const;

export type IconName = keyof typeof PATHS;

export function Icon({ name, size = 24, className }: { name: IconName; size?: number; className?: string }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="square"
      strokeLinejoin="miter"
      aria-hidden="true"
      className={className}
    >
      <path d={PATHS[name]} />
    </svg>
  );
}
