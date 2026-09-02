import React from "react";

export interface RadarDatum {
  label: string;
  value: number; // 0..1
  color: string; // hex, e.g. "#7B9E7A"
}

interface Props {
  data: RadarDatum[];
  size?: number;
}

// Lightweight dependency-free SVG radar chart for the 8 emotional fluids.
export default function FluidRadar({ data, size = 240 }: Props) {
  const cx = size / 2;
  const cy = size / 2;
  const radius = size / 2 - 38; // leave room for labels
  const n = Math.max(data.length, 3);

  const angleFor = (i: number) => (Math.PI * 2 * i) / n - Math.PI / 2;
  const point = (i: number, r: number): [number, number] => {
    const a = angleFor(i);
    return [cx + Math.cos(a) * r, cy + Math.sin(a) * r];
  };

  const rings = [0.25, 0.5, 0.75, 1];
  const ringPolys = rings.map((r) =>
    data.map((_, i) => point(i, radius * r).join(",")).join(" ")
  );

  const safeVal = (v: number) => Math.max(0, Math.min(1, v || 0));
  const dataPoints = data.map((d, i) => point(i, radius * safeVal(d.value)));
  const dataPoly = dataPoints.map((p) => p.join(",")).join(" ");

  return (
    <div className="flex flex-col items-center">
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="max-w-full"
        role="img"
        aria-label="Emotional fluid radar"
      >
        {/* grid rings */}
        {ringPolys.map((poly, idx) => (
          <polygon
            key={idx}
            points={poly}
            fill="none"
            stroke="var(--c-border)"
            strokeWidth={1}
          />
        ))}
        {/* spokes */}
        {data.map((_, i) => {
          const [x, y] = point(i, radius);
          return (
            <line
              key={i}
              x1={cx}
              y1={cy}
              x2={x}
              y2={y}
              stroke="var(--c-border)"
              strokeWidth={1}
            />
          );
        })}
        {/* data polygon */}
        <polygon
          points={dataPoly}
          fill="var(--c-accent)"
          fillOpacity={0.16}
          stroke="var(--c-accent)"
          strokeWidth={2}
          strokeLinejoin="round"
          style={{
            transition: "all 0.6s cubic-bezier(0.4, 0, 0.2, 1)",
            filter: "drop-shadow(0 0 6px color-mix(in srgb, var(--c-accent) 35%, transparent))",
          }}
        />
        {/* vertices */}
        {dataPoints.map((p, i) => (
          <circle
            key={i}
            cx={p[0]}
            cy={p[1]}
            r={3.5}
            fill={data[i].color}
            stroke="var(--c-white)"
            strokeWidth={1.5}
            style={{
              transition: "all 0.6s cubic-bezier(0.4, 0, 0.2, 1)",
              filter: `drop-shadow(0 0 4px ${data[i].color}88)`,
            }}
          >
            <animate
              attributeName="r"
              values="3.5;5;3.5"
              dur="2.4s"
              begin={`${i * 0.15}s`}
              repeatCount="indefinite"
            />
          </circle>
        ))}
        {/* labels */}
        {data.map((d, i) => {
          const [x, y] = point(i, radius + 16);
          const cos = Math.cos(angleFor(i));
          const anchor = cos > 0.15 ? "start" : cos < -0.15 ? "end" : "middle";
          const pct = Math.round(safeVal(d.value) * 100);
          return (
            <text
              key={i}
              x={x}
              y={y}
              textAnchor={anchor}
              dominantBaseline="middle"
              fill="var(--c-secondary)"
              style={{ fontSize: 10, fontWeight: 600 }}
            >
              {d.label} {pct}%
            </text>
          );
        })}
      </svg>

      {/* compact readout bars */}
      <div className="w-full mt-2 space-y-1.5">
        {data.map((d, i) => {
          const pct = Math.round(safeVal(d.value) * 100);
          return (
            <div key={i} className="flex items-center gap-2 group">
              <span
                className="inline-block w-2.5 h-2.5 rounded-full shrink-0 transition-transform group-hover:scale-125"
                style={{ backgroundColor: d.color }}
              />
              <span className="text-[10px] text-[var(--c-secondary)] w-16 shrink-0 truncate">{d.label}</span>
              <span className="flex-1 h-1.5 rounded-full bg-[var(--c-border)] overflow-hidden">
                <span
                  className="block h-full rounded-full"
                  style={{
                    width: `${pct}%`,
                    backgroundColor: d.color,
                    transition: "width 0.8s cubic-bezier(0.4, 0, 0.2, 1)",
                  }}
                />
              </span>
              <span className="text-[10px] font-mono text-[var(--c-muted)] w-8 text-right">{pct}%</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
