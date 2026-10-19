import React from 'react';

interface ChefMintLogoProps {
  className?: string;
  size?: number;
  showText?: boolean;
  textClassName?: string;
}

export const ChefMintLogo: React.FC<ChefMintLogoProps> = ({
  className = 'w-9 h-9',
  size,
  showText = false,
  textClassName = 'text-xl font-extrabold text-emerald-950 tracking-tight',
}) => {
  const style = size ? { width: `${size}px`, height: `${size}px` } : undefined;

  return (
    <div className="inline-flex items-center gap-2 select-none">
      <svg
        viewBox="0 0 120 120"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className={`${className} shrink-0`}
        style={style}
      >
        <defs>
          <linearGradient id="chefmintStroke" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#34D399" />
            <stop offset="100%" stopColor="#059669" />
          </linearGradient>
          <linearGradient id="leafGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#10B981" />
            <stop offset="100%" stopColor="#047857" />
          </linearGradient>
          <filter id="mintGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="2" stdDeviation="2" floodColor="#10B981" floodOpacity="0.25" />
          </filter>
        </defs>

        {/* Chef Hat Base Brims */}
        <path
          d="M26 80 H68 M26 87 H68"
          stroke="url(#chefmintStroke)"
          strokeWidth="5"
          strokeLinecap="round"
        />

        {/* Chef Hat Puff Outline (Exact silhouette from banner) */}
        <path
          d="M26 80 C 22 62, 10 54, 16 40 C 20 28, 32 30, 38 36 C 42 18, 58 14, 66 26 C 74 16, 88 26, 84 44 C 86 54, 76 64, 68 80"
          stroke="url(#chefmintStroke)"
          strokeWidth="5.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="none"
          filter="url(#mintGlow)"
        />

        {/* Pleat details */}
        <path
          d="M38 74 V 54 M50 74 V 48 M62 74 V 54"
          stroke="#10B981"
          strokeWidth="3"
          strokeLinecap="round"
          opacity="0.3"
        />

        {/* Sprouting Mint Leaf on the Right (Distinctive Brand Mark) */}
        <g transform="translate(62, 46)">
          <path
            d="M2 36 C 4 20, 16 10, 38 4 C 34 24, 26 38, 2 36 Z"
            fill="url(#leafGrad)"
            stroke="#047857"
            strokeWidth="2.5"
            strokeLinejoin="round"
          />
          {/* Main Leaf Vein */}
          <path
            d="M4 35 Q 18 22 36 5"
            stroke="#ECFDF5"
            strokeWidth="2.2"
            strokeLinecap="round"
          />
          {/* Subtle Branching Veins */}
          <path
            d="M12 27 Q 18 29 22 32 M18 20 Q 24 21 28 24 M24 14 Q 29 14 32 16"
            stroke="#ECFDF5"
            strokeWidth="1.3"
            strokeLinecap="round"
            opacity="0.9"
          />
        </g>
      </svg>

      {showText && (
        <span className={textClassName}>
          Chef<span className="text-emerald-600">Mint</span> AI
        </span>
      )}
    </div>
  );
};
