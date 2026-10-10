// Studio-Verlauf mit animierten Signallinien. Erscheint, solange es keine Auto-Frames gibt.
// Warum: Die Seite sieht auch ohne Video-Lieferung gut aus und bricht nie.
export function SignalFallback() {
  return (
    <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_30%_40%,#16202e_0%,#0a0a0b_70%)]" aria-hidden="true">
      <svg viewBox="0 0 1000 600" preserveAspectRatio="xMidYMid slice" className="h-full w-full opacity-60">
        {[0, 1, 2, 3, 4, 5].map((i) => (
          <path
            key={i}
            className="signal-line"
            d={`M0 ${120 + i * 70} C250 ${60 + i * 80} 450 ${260 + i * 40} 700 ${180 + i * 60} S900 ${120 + i * 50} 1000 ${150 + i * 60}`}
            fill="none"
            stroke={i % 3 === 0 ? "#81c4ff" : i % 3 === 1 ? "#1c69d4" : "#16588e"}
            strokeWidth="1"
            style={{ animationDelay: `${i * -1.2}s` }}
          />
        ))}
      </svg>
    </div>
  );
}
