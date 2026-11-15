import { ImageResponse } from "next/og";

export const size = { width: 32, height: 32 };
export const contentType = "image/png";

// The hero's object at tab size: a four-panel folding screen, a gold zigzag on the azurite ground.
export default function Icon() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "#6581df",
          borderRadius: 7,
        }}
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <polyline
            points="3,7 9,4 15,7 21,4 21,19 15,22 9,19 3,22 3,7"
            fill="#d9b45a"
            stroke="#8c6a1f"
            strokeWidth="1"
            strokeLinejoin="round"
          />
          <path d="M9 4v15M15 7v15" stroke="#8c6a1f" strokeWidth="1" />
        </svg>
      </div>
    ),
    { ...size }
  );
}
