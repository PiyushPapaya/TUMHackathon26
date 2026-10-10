"use client";

import { useEffect, useRef } from "react";

const VERTEX_SRC = `
attribute vec2 a_position;
void main() {
  gl_Position = vec4(a_position, 0.0, 1.0);
}
`;

// Weicher, langsamer Verlauf aus Value-Noise statt teurer Simplex-Noise:
// reicht für einen ruhigen Hintergrund und kostet kaum GPU-Zeit.
const FRAGMENT_SRC = `
precision highp float;
uniform vec2 u_resolution;
uniform float u_time;

float hash(vec2 p) {
  return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
}

float noise(vec2 p) {
  vec2 i = floor(p);
  vec2 f = fract(p);
  vec2 u = f * f * (3.0 - 2.0 * f);
  return mix(
    mix(hash(i), hash(i + vec2(1.0, 0.0)), u.x),
    mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x),
    u.y
  );
}

void main() {
  vec2 uv = gl_FragCoord.xy / u_resolution.xy;
  vec2 p = uv * 3.0;

  float n = 0.0;
  n += noise(p + u_time * 0.05) * 0.6;
  n += noise(p * 2.0 - u_time * 0.08) * 0.4;

  // Signal2Spec-Markenfarben: dunkles Navy (#0b1f3a) bis gedecktes Blau.
  vec3 colorA = vec3(0.043, 0.122, 0.227);
  vec3 colorB = vec3(0.145, 0.239, 0.396);
  vec3 color = mix(colorA, colorB, n);

  gl_FragColor = vec4(color, 1.0);
}
`;

function compileShader(gl: WebGLRenderingContext, type: number, source: string) {
  const shader = gl.createShader(type);
  if (!shader) throw new Error("createShader fehlgeschlagen");
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    const info = gl.getShaderInfoLog(shader);
    gl.deleteShader(shader);
    throw new Error(info ?? "Shader-Kompilierung fehlgeschlagen");
  }
  return shader;
}

/**
 * Animierter WebGL-Verlauf als Seitenhintergrund (fixed, hinter dem Inhalt).
 * Läuft nur im Browser (kein SSR für WebGL); ohne WebGL bleibt die Seite
 * einfach beim CSS-Hintergrund aus globals.css.
 */
export function ShaderBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const gl = canvas.getContext("webgl", { antialias: false, depth: false });
    if (!gl) return;

    const vertexShader = compileShader(gl, gl.VERTEX_SHADER, VERTEX_SRC);
    const fragmentShader = compileShader(gl, gl.FRAGMENT_SHADER, FRAGMENT_SRC);

    const program = gl.createProgram();
    if (!program) return;
    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      console.error(gl.getProgramInfoLog(program));
      return;
    }
    gl.useProgram(program);

    // Vollbild-Quad aus zwei Dreiecken (kein Element-Buffer nötig).
    const positionBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
    gl.bufferData(
      gl.ARRAY_BUFFER,
      new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]),
      gl.STATIC_DRAW,
    );

    const positionLoc = gl.getAttribLocation(program, "a_position");
    gl.enableVertexAttribArray(positionLoc);
    gl.vertexAttribPointer(positionLoc, 2, gl.FLOAT, false, 0, 0);

    const resolutionLoc = gl.getUniformLocation(program, "u_resolution");
    const timeLoc = gl.getUniformLocation(program, "u_time");

    const start = performance.now();
    let animationFrame = 0;

    function resize() {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const width = Math.floor(window.innerWidth * dpr);
      const height = Math.floor(window.innerHeight * dpr);
      if (canvas && (canvas.width !== width || canvas.height !== height)) {
        canvas.width = width;
        canvas.height = height;
        gl?.viewport(0, 0, width, height);
      }
    }

    function render(now: number) {
      resize();
      gl!.uniform2f(resolutionLoc, canvas!.width, canvas!.height);
      gl!.uniform1f(timeLoc, (now - start) / 1000);
      gl!.drawArrays(gl!.TRIANGLES, 0, 6);
      animationFrame = requestAnimationFrame(render);
    }

    resize();
    animationFrame = requestAnimationFrame(render);
    window.addEventListener("resize", resize);

    return () => {
      cancelAnimationFrame(animationFrame);
      window.removeEventListener("resize", resize);
      gl.deleteProgram(program);
      gl.deleteShader(vertexShader);
      gl.deleteShader(fragmentShader);
      gl.deleteBuffer(positionBuffer);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="pointer-events-none fixed inset-0 -z-10 h-full w-full"
      aria-hidden="true"
    />
  );
}
