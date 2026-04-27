export default function HeroImage() {
  return (
    <svg
      viewBox="0 0 200 200"
      aria-hidden
      overflow="visible"
      className="absolute inset-0 w-full h-full select-none pointer-events-none"
    >
      <defs>
        <linearGradient id="laptop-stroke" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="var(--secondary)" />
          <stop offset="100%" stopColor="var(--primary)" />
        </linearGradient>
        <filter id="laptop-glow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="1.8" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      <g
        className="laptop"
        stroke="url(#laptop-stroke)"
        strokeWidth="1.5"
        strokeLinecap="butt"
        strokeLinejoin="round"
        fill="none"
        filter="url(#laptop-glow)"
      >
        <path
          className="laptop__lid"
          pathLength={1}
          d="M100 32 L154 32 Q162 32 162 40 L162 100 Q162 104 158 104 L42 104 Q38 104 38 100 L38 40 Q38 32 46 32 L100 32 Z"
        />
        <path
          className="laptop__deck"
          pathLength={1}
          d="M100 110 L161 110 Q167 110 169 115.7 L174 130.3 Q176 136 170 136 L30 136 Q24 136 26 130.3 L31 115.7 Q33 110 39 110 L100 110 Z"
        />
        <path
          className="laptop__bevel"
          pathLength={1}
          d="M100 142 L172 142 Q176 142 178 145.4 L180 148.6 Q182 152 178 152 L22 152 Q18 152 20 148.6 L22 145.4 Q24 142 28 142 L100 142 Z"
        />
        <path
          className="laptop__screen"
          pathLength={1}
          d="M100 44 L150 44 Q152 44 152 46 L152 90 Q152 92 150 92 L50 92 Q48 92 48 90 L48 46 Q48 44 50 44 L100 44 Z"
        />
        <circle
          className="laptop__camera"
          cx={100}
          cy={38}
          r={0.9}
          fill="url(#laptop-stroke)"
          stroke="none"
        />
        <path
          className="laptop__trackpad"
          pathLength={1}
          d="M100 122 L112 122 Q114 122 114.7 123.9 L116.3 128.1 Q117 130 115 130 L85 130 Q83 130 83.7 128.1 L85.3 123.9 Q86 122 88 122 L100 122 Z"
        />
        <path
          className="laptop__shadow"
          pathLength={1}
          strokeWidth={2}
          d="M55 162 Q100 167 145 162"
        />
      </g>
    </svg>
  );
}
