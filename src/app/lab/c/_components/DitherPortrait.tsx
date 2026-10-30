"use client";

import Image from "next/image";
import { useEffect, useRef } from "react";

// The one shader moment: the portrait is printed as an 8×8 ordered dither in the
// ink colour, and a loupe "develops" the true-colour photo under the pointer.

const VERT = `
attribute vec2 aPos;
varying vec2 vUv;
void main() {
  vUv = aPos * 0.5 + 0.5;
  gl_Position = vec4(aPos, 0.0, 1.0);
}`;

const FRAG = `
precision highp float;
varying vec2 vUv;
uniform sampler2D uTex;
uniform vec2 uRes;
uniform vec2 uLens;
uniform float uRadius;
uniform float uCell;
uniform float uReveal;
uniform vec3 uInk;

float bayer2(vec2 a) { a = floor(a); return fract(a.x * 0.5 + a.y * a.y * 0.75); }
float bayer4(vec2 a) { return bayer2(0.5 * a) * 0.25 + bayer2(a); }
float bayer8(vec2 a) { return bayer4(0.5 * a) * 0.25 + bayer2(a); }

void main() {
  vec2 px = gl_FragCoord.xy;
  vec2 cell = floor(px / uCell);
  vec4 s = texture2D(uTex, (cell + 0.5) * uCell / uRes);
  float lum = dot(s.rgb, vec3(0.299, 0.587, 0.114));
  lum = clamp((lum - 0.2) * 1.3, 0.0, 1.0);
  float on = step(bayer8(cell), lum) * step(0.5, s.a);
  vec4 print = vec4(uInk * on, on);

  float d = distance(px, uLens);
  float m = (1.0 - smoothstep(uRadius * 0.86, uRadius, d)) * uReveal;
  vec2 dir = normalize(px - uLens + 0.0001);
  vec2 off = dir * smoothstep(uRadius * 0.45, uRadius, d) * 7.0 / uRes;
  vec4 c = texture2D(uTex, vUv);
  float r = texture2D(uTex, vUv + off).r;
  float b = texture2D(uTex, vUv - off).b;
  vec4 photo = vec4(vec3(r, c.g, b) * c.a, c.a);

  float ring = (1.0 - smoothstep(0.0, 1.25, abs(d - uRadius))) * uReveal;
  vec4 col = mix(print, photo, m);
  gl_FragColor = mix(col, vec4(uInk, 1.0), ring);
}`;

function hexToRgb(hex: string): [number, number, number] {
  const n = parseInt(hex.slice(1), 16);
  return [((n >> 16) & 255) / 255, ((n >> 8) & 255) / 255, (n & 255) / 255];
}

function compile(gl: WebGLRenderingContext, type: number, src: string) {
  const s = gl.createShader(type)!;
  gl.shaderSource(s, src);
  gl.compileShader(s);
  return s;
}

type Props = { src: string; ink: string; alt: string };

export default function DitherPortrait({ src, ink, alt }: Props) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const wrap = wrapRef.current;
    const canvas = canvasRef.current;
    if (!wrap || !canvas) return;
    const gl = canvas.getContext("webgl", { antialias: false, premultipliedAlpha: true });
    if (!gl) return;

    // `?still` freezes the lens over the face (for reviews and screenshots).
    const still = new URLSearchParams(window.location.search).has("still");
    const reduce = still || matchMedia("(prefers-reduced-motion: reduce)").matches;
    const coarse = matchMedia("(pointer: coarse)").matches;
    const dpr = Math.min(window.devicePixelRatio || 1, coarse ? 1.5 : 2);

    const prog = gl.createProgram()!;
    gl.attachShader(prog, compile(gl, gl.VERTEX_SHADER, VERT));
    gl.attachShader(prog, compile(gl, gl.FRAGMENT_SHADER, FRAG));
    gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) return;
    gl.useProgram(prog);

    gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    const aPos = gl.getAttribLocation(prog, "aPos");
    gl.enableVertexAttribArray(aPos);
    gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 0, 0);

    const u = (name: string) => gl.getUniformLocation(prog, name);
    const uRes = u("uRes"), uLens = u("uLens"), uRadius = u("uRadius");
    const uCell = u("uCell"), uReveal = u("uReveal");
    gl.uniform3fv(u("uInk"), hexToRgb(ink));
    gl.clearColor(0, 0, 0, 0);

    let w = 0, h = 0;
    let ready = false, visible = true, raf = 0;
    let pointerAt = -Infinity;
    const lens = { x: 0, y: 0 }, target = { x: 0, y: 0 };
    let reveal = 0;
    const start = performance.now();

    const draw = () => {
      gl.uniform2f(uRes, canvas.width, canvas.height);
      gl.uniform2f(uLens, lens.x * dpr, (h - lens.y) * dpr);
      gl.uniform1f(uRadius, w * (coarse ? 0.26 : 0.22) * dpr);
      gl.uniform1f(uCell, (coarse ? 2.5 : 3) * dpr);
      gl.uniform1f(uReveal, reveal);
      gl.clear(gl.COLOR_BUFFER_BIT);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    };

    const idleTarget = (t: number) => {
      const s = t / 1000;
      target.x = w * (0.47 + 0.17 * Math.sin(s * 0.41));
      target.y = h * (0.42 + 0.13 * Math.sin(s * 0.67 + 1.3));
    };

    const tick = (now: number) => {
      raf = 0;
      if (!ready || !visible) return;
      const pointing = now - pointerAt < 1400;
      if (!pointing) idleTarget(now - start);
      lens.x += (target.x - lens.x) * 0.1;
      lens.y += (target.y - lens.y) * 0.1;
      const k = Math.min(Math.max((now - start - 700) / 900, 0), 1);
      reveal = k * k * (3 - 2 * k);
      draw();
      raf = requestAnimationFrame(tick);
    };

    const kick = () => {
      if (reduce) return draw();
      if (!raf) raf = requestAnimationFrame(tick);
    };

    const resize = () => {
      const r = wrap.getBoundingClientRect();
      w = r.width;
      h = r.height;
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
      gl.viewport(0, 0, canvas.width, canvas.height);
      if (!lens.x) {
        idleTarget(0);
        lens.x = target.x;
        lens.y = target.y;
      }
      if (ready) kick();
    };

    const onPointer = (e: PointerEvent) => {
      const r = wrap.getBoundingClientRect();
      target.x = e.clientX - r.left;
      target.y = e.clientY - r.top;
      pointerAt = performance.now();
      if (reduce) {
        lens.x = target.x;
        lens.y = target.y;
        reveal = 1;
      }
      kick();
    };
    const onLeave = () => {
      if (reduce) {
        reveal = 0;
        draw();
      }
    };

    const img = new window.Image();
    img.onload = () => {
      gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
      gl.bindTexture(gl.TEXTURE_2D, gl.createTexture());
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, img);
      ready = true;
      wrap.dataset.gl = "on";
      if (still) reveal = 1;
      kick();
    };
    img.src = src;

    const ro = new ResizeObserver(resize);
    ro.observe(wrap);
    const io = new IntersectionObserver(([entry]) => {
      visible = entry.isIntersecting;
      if (visible) kick();
    });
    io.observe(wrap);
    wrap.addEventListener("pointermove", onPointer);
    wrap.addEventListener("pointerdown", onPointer);
    wrap.addEventListener("pointerleave", onLeave);

    return () => {
      cancelAnimationFrame(raf);
      ro.disconnect();
      io.disconnect();
      wrap.removeEventListener("pointermove", onPointer);
      wrap.removeEventListener("pointerdown", onPointer);
      wrap.removeEventListener("pointerleave", onLeave);
    };
  }, [src, ink]);

  return (
    <div
      ref={wrapRef}
      className="group relative aspect-430/448 w-full touch-pan-y select-none"
    >
      {/* Fallback (no WebGL) and first paint: an ink-tinted duotone of the same cutout. */}
      <div className="absolute inset-0 group-data-[gl=on]:invisible">
        <Image
          src={src}
          alt={alt}
          fill
          priority
          sizes="(min-width: 768px) 40vw, 100vw"
          className="object-contain grayscale contrast-125"
        />
        <div
          aria-hidden
          className="absolute inset-0 mix-blend-multiply"
          style={{
            backgroundColor: ink,
            maskImage: `url(${src})`,
            maskSize: "contain",
            maskRepeat: "no-repeat",
            maskPosition: "center",
          }}
        />
      </div>
      <canvas
        ref={canvasRef}
        aria-hidden
        className="absolute inset-0 h-full w-full opacity-0 transition-opacity duration-500 group-data-[gl=on]:opacity-100"
      />
    </div>
  );
}
