"use client";

import Image from "next/image";
import { useEffect, useRef, useState } from "react";
import styles from "../b.module.css";

// The portrait rebuilt as a point cloud: one particle per sampled pixel,
// colour from the photo, depth from luminance. Pointer parallax + local
// displacement; scrolling past the hero streams the cloud away.

const VERT = /* glsl */ `
attribute vec3 aPos;
attribute vec3 aColor;
attribute float aSeed;

uniform float uTime;
uniform float uIntro;
uniform float uScatter;
uniform float uSize;
uniform vec2 uMouse;
uniform vec2 uRot;
uniform vec2 uCenter;
uniform float uScale;
uniform float uAspect;
uniform vec3 uAccent;

varying vec3 vColor;
varying float vAlpha;

void main() {
  vec3 p = aPos;

  // Assemble from a loose cloud on load; each particle lands at its own time.
  float t = clamp(uIntro * 1.5 - aSeed * 0.5, 0.0, 1.0);
  t = 1.0 - pow(1.0 - t, 3.0);
  vec3 origin = (vec3(fract(aSeed * 91.37), fract(aSeed * 47.13), fract(aSeed * 13.71)) - 0.5)
    * vec3(5.0, 3.5, 3.0);
  p = mix(origin, p, t);

  // Breathing.
  p.z += sin(uTime * 0.7 + aSeed * 6.2831) * 0.02;
  p.xy += vec2(sin(uTime * 0.5 + aSeed * 40.0), cos(uTime * 0.6 + aSeed * 30.0)) * 0.004;

  // Pointer: push particles away from the cursor and toward the camera.
  vec2 d = p.xy - uMouse;
  float dist = length(d);
  float f = smoothstep(0.32, 0.0, dist) * t;
  p.xy += (d / max(dist, 1e-3)) * f * 0.1;
  p.z += f * 0.35;

  // Scroll: stream down and outward, each particle on its own trajectory.
  float s = uScatter * uScatter;
  vec3 dir = vec3(
    (fract(aSeed * 12.9898) - 0.5) * 1.6,
    -0.6 - fract(aSeed * 78.233) * 1.4,
    (fract(aSeed * 37.719) - 0.3) * 1.2
  );
  p += dir * s * (1.2 + aSeed * 1.8);

  // Rotate (yaw, then pitch).
  float cy = cos(uRot.x), sy = sin(uRot.x);
  p = vec3(cy * p.x + sy * p.z, p.y, -sy * p.x + cy * p.z);
  float cx = cos(uRot.y), sx = sin(uRot.y);
  p = vec3(p.x, cx * p.y - sx * p.z, sx * p.y + cx * p.z);

  float persp = 3.2 / (3.2 - p.z);
  vec2 ndc = uCenter + vec2(p.x * uScale / uAspect, p.y * uScale) * persp;
  gl_Position = vec4(ndc, 0.0, 1.0);
  gl_PointSize = uSize * persp * (1.0 + f * 0.8);

  vColor = mix(aColor, uAccent, f * 0.85);
  // Fade out the photo's hard bottom crop, and the cloud as it streams away.
  float edge = smoothstep(-1.0, -0.55, aPos.y);
  vAlpha = t * mix(edge, 1.0, uScatter) * (1.0 - smoothstep(0.55, 1.0, uScatter));
}
`;

const FRAG = /* glsl */ `
precision mediump float;
varying vec3 vColor;
varying float vAlpha;

void main() {
  float d = length(gl_PointCoord - 0.5);
  if (d > 0.5) discard;
  gl_FragColor = vec4(vColor, smoothstep(0.5, 0.25, d) * vAlpha);
}
`;

const ACCENT: [number, number, number] = [0xf2 / 255, 0xb5 / 255, 0x44 / 255];
const BONE: [number, number, number] = [0xeb / 255, 0xe6 / 255, 0xdc / 255];

type Cloud = { pos: Float32Array; color: Float32Array; seed: Float32Array; count: number };

function sampleImage(img: HTMLImageElement, step: number): Cloud {
  const w = img.naturalWidth;
  const h = img.naturalHeight;
  const c = document.createElement("canvas");
  c.width = w;
  c.height = h;
  const ctx = c.getContext("2d", { willReadFrequently: true })!;
  ctx.drawImage(img, 0, 0);
  const data = ctx.getImageData(0, 0, w, h).data;
  const aspect = w / h;
  const pos: number[] = [];
  const color: number[] = [];
  const seed: number[] = [];

  for (let y = 0; y < h; y += step) {
    for (let x = 0; x < w; x += step) {
      const i = (y * w + x) * 4;
      if (data[i + 3] < 150) continue;
      // Lift shadows a touch and warm toward bone so the dark jacket and hair
      // still read on near-black without flattening the face.
      const rgb = [data[i], data[i + 1], data[i + 2]].map((v, k) => {
        const lifted = Math.pow(v / 255, 0.85);
        return Math.min(1, lifted * 1.04 + BONE[k] * 0.05);
      });
      const lum = 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2];
      const jx = (Math.random() - 0.5) * step;
      const jy = (Math.random() - 0.5) * step;
      pos.push(((x + jx) / w - 0.5) * 2 * aspect, -((y + jy) / h - 0.5) * 2, (lum - 0.45) * 0.55);
      color.push(rgb[0], rgb[1], rgb[2]);
      seed.push(Math.random());
    }
  }

  return {
    pos: new Float32Array(pos),
    color: new Float32Array(color),
    seed: new Float32Array(seed),
    count: seed.length,
  };
}

function compile(gl: WebGLRenderingContext, type: number, src: string) {
  const s = gl.createShader(type)!;
  gl.shaderSource(s, src);
  gl.compileShader(s);
  if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
    throw new Error(gl.getShaderInfoLog(s) ?? "shader compile failed");
  }
  return s;
}

function setup(gl: WebGLRenderingContext, cloud: Cloud) {
  const prog = gl.createProgram()!;
  gl.attachShader(prog, compile(gl, gl.VERTEX_SHADER, VERT));
  gl.attachShader(prog, compile(gl, gl.FRAGMENT_SHADER, FRAG));
  gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
    throw new Error(gl.getProgramInfoLog(prog) ?? "program link failed");
  }
  gl.useProgram(prog);

  const attr = (name: string, data: Float32Array, size: number) => {
    const buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, data, gl.STATIC_DRAW);
    const loc = gl.getAttribLocation(prog, name);
    gl.enableVertexAttribArray(loc);
    gl.vertexAttribPointer(loc, size, gl.FLOAT, false, 0, 0);
  };
  attr("aPos", cloud.pos, 3);
  attr("aColor", cloud.color, 3);
  attr("aSeed", cloud.seed, 1);

  gl.enable(gl.BLEND);
  gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
  gl.clearColor(0, 0, 0, 0);

  const u = (name: string) => gl.getUniformLocation(prog, name);
  const uniforms = {
    time: u("uTime"),
    intro: u("uIntro"),
    scatter: u("uScatter"),
    size: u("uSize"),
    mouse: u("uMouse"),
    rot: u("uRot"),
    center: u("uCenter"),
    scale: u("uScale"),
    aspect: u("uAspect"),
  };
  gl.uniform3fv(u("uAccent"), ACCENT);
  return uniforms;
}

// Where the cloud sits: right half on desktop, top half on phones.
function layout(w: number, h: number) {
  if (w < 768) return { cx: 0, cy: 0.4, scale: Math.min(0.52, (w / h) * 1.1) };
  return { cx: 0.44, cy: -0.02, scale: 0.8 };
}

export default function ParticlePortrait({ src }: { src: string }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [fallback, setFallback] = useState(false);

  useEffect(() => {
    const canvas = canvasRef.current!;
    let disposed = false;
    let cleanup = () => {};

    const img = new window.Image();
    img.decoding = "async";
    img.src = src;
    img.onerror = () => !disposed && setFallback(true);
    img.onload = () => {
      if (disposed) return;
      const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      const gl = reduce
        ? null
        : canvas.getContext("webgl", {
            alpha: true,
            antialias: false,
            premultipliedAlpha: false,
            powerPreference: "high-performance",
          });
      if (!gl) {
        setFallback(true);
        return;
      }

      const small = window.innerWidth < 768;
      const cloud = sampleImage(img, small ? 3 : 2);
      let uniforms: ReturnType<typeof setup>;
      try {
        uniforms = setup(gl, cloud);
      } catch {
        setFallback(true);
        return;
      }

      const coarse = window.matchMedia("(pointer: coarse)").matches;
      const state = {
        w: 0,
        h: 0,
        dpr: 1,
        mouse: [9, 9],
        mouseTarget: [9, 9],
        rot: [0, 0],
        rotTarget: [0, 0],
        scatter: 0,
        start: performance.now(),
        lost: false,
        raf: 0,
      };

      const resize = () => {
        state.dpr = Math.min(window.devicePixelRatio || 1, small ? 1.5 : 2);
        state.w = window.innerWidth;
        state.h = window.innerHeight;
        canvas.width = Math.round(state.w * state.dpr);
        canvas.height = Math.round(state.h * state.dpr);
        gl.viewport(0, 0, canvas.width, canvas.height);
        kick();
      };

      const readScroll = () => {
        state.scatter = Math.min(1, Math.max(0, window.scrollY / (state.h * 0.85)));
        canvas.style.visibility = state.scatter >= 1 ? "hidden" : "visible";
        kick();
      };

      const onPointer = (e: PointerEvent) => {
        if (e.pointerType !== "mouse") return;
        const { cx, cy, scale } = layout(state.w, state.h);
        const nx = (e.clientX / state.w) * 2 - 1;
        const ny = -((e.clientY / state.h) * 2 - 1);
        state.mouseTarget = [((nx - cx) * (state.w / state.h)) / scale, (ny - cy) / scale];
        state.rotTarget = [(nx - cx) * 0.35, -(ny - cy) * 0.2];
        kick();
      };
      const onLeave = () => {
        state.mouseTarget = [9, 9];
        state.rotTarget = [0, 0];
      };

      const frame = (now: number) => {
        state.raf = 0;
        const elapsed = (now - state.start) / 1000;
        const intro = Math.min(1, elapsed / 1.8);

        if (coarse) state.rotTarget = [Math.sin(elapsed * 0.35) * 0.18, Math.sin(elapsed * 0.27) * 0.06];
        const k = 0.08;
        state.mouse[0] += (state.mouseTarget[0] - state.mouse[0]) * k;
        state.mouse[1] += (state.mouseTarget[1] - state.mouse[1]) * k;
        state.rot[0] += (state.rotTarget[0] - state.rot[0]) * 0.05;
        state.rot[1] += (state.rotTarget[1] - state.rot[1]) * 0.05;

        const { cx, cy, scale } = layout(state.w, state.h);
        gl.clear(gl.COLOR_BUFFER_BIT);
        gl.uniform1f(uniforms.time, elapsed);
        gl.uniform1f(uniforms.intro, intro);
        gl.uniform1f(uniforms.scatter, state.scatter);
        gl.uniform1f(uniforms.size, (small ? 2.2 : 3.1) * state.dpr);
        gl.uniform2f(uniforms.mouse, state.mouse[0], state.mouse[1]);
        gl.uniform2f(uniforms.rot, state.rot[0], state.rot[1]);
        gl.uniform2f(uniforms.center, cx, cy);
        gl.uniform1f(uniforms.scale, scale);
        gl.uniform1f(uniforms.aspect, state.w / state.h);
        gl.drawArrays(gl.POINTS, 0, cloud.count);

        kick();
      };

      function kick() {
        if (state.raf || state.lost || document.hidden || state.scatter >= 1) return;
        state.raf = requestAnimationFrame(frame);
      }

      const onLost = (e: Event) => {
        e.preventDefault();
        state.lost = true;
        cancelAnimationFrame(state.raf);
        state.raf = 0;
      };
      const onRestored = () => {
        try {
          uniforms = setup(gl, cloud);
        } catch {
          setFallback(true);
          return;
        }
        state.lost = false;
        resize();
      };

      window.addEventListener("resize", resize);
      window.addEventListener("scroll", readScroll, { passive: true });
      window.addEventListener("pointermove", onPointer, { passive: true });
      document.documentElement.addEventListener("pointerleave", onLeave);
      document.addEventListener("visibilitychange", kick);
      canvas.addEventListener("webglcontextlost", onLost);
      canvas.addEventListener("webglcontextrestored", onRestored);
      resize();
      readScroll();

      cleanup = () => {
        cancelAnimationFrame(state.raf);
        window.removeEventListener("resize", resize);
        window.removeEventListener("scroll", readScroll);
        window.removeEventListener("pointermove", onPointer);
        document.documentElement.removeEventListener("pointerleave", onLeave);
        document.removeEventListener("visibilitychange", kick);
        canvas.removeEventListener("webglcontextlost", onLost);
        canvas.removeEventListener("webglcontextrestored", onRestored);
      };
    };

    return () => {
      disposed = true;
      cleanup();
    };
  }, [src]);

  return (
    <>
      <canvas ref={canvasRef} className={styles.canvas} aria-hidden />
      {fallback && (
        <div className={styles.staticPortrait} aria-hidden>
          <Image src={src} alt="" fill sizes="(min-width: 768px) 46vw, 72vw" priority />
        </div>
      )}
    </>
  );
}
