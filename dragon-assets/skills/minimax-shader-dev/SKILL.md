---
license: UNKNOWN
---

# MiniMax Shader Development Skill

## Overview

GLSL shader development covering 36 ShaderToy-compatible techniques for real-time visual effects, ray marching, fluid simulation, and procedural generation.

## Invocation

```
/minimax-shader "实现光线行进着色器"
[@13-01] 使用shader-dev创建3D场景
[@10-03] 使用shader-dev实现流体模拟
```

## Core Structure

```
skills/
├── techniques/          # Implementation guides
├── reference/           # Advanced documentation
└── SKILL.md            # This file
```

## Key Technique Categories

### Geometry & SDF (Signed Distance Functions)

```glsl
// 2D SDF
float sdCircle(vec2 p, float r) {
  return length(p) - r;
}

float sdBox(vec2 p, vec2 b) {
  vec2 d = abs(p) - b;
  return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0);
}

// 3D SDF
float sdSphere(vec3 p, float r) {
  return length(p) - r;
}

float sdBox(vec3 p, vec3 b) {
  vec3 q = abs(p) - b;
  return length(max(q, 0.0)) + min(max(q.x, max(q.y, q.z)), 0.0);
}

// CSG Boolean Operations
float opUnion(float d1, float d2) { return min(d1, d2); }
float opSubtraction(float d1, float d2) { return max(-d1, d2); }
float opIntersection(float d1, float d2) { return max(d1, d2); }
float opSmoothUnion(float d1, float d2, float k) {
  float h = clamp(0.5 + 0.5 * (d2 - d1) / k, 0.0, 1.0);
  return mix(d2, d1, h) - k * h * (1.0 - h);
}
```

### Ray Marching

```glsl
#define MAX_STEPS 128
#define MAX_DIST 100.0
#define SURF_DIST 0.001

float rayMarch(vec3 ro, vec3 rd) {
  float d = 0.0;
  for(int i = 0; i < MAX_STEPS; i++) {
    vec3 p = ro + rd * d;
    float ds = map(p);
    d += ds;
    if(ds < SURF_DIST || d > MAX_DIST) break;
  }
  return d;
}

vec3 calcNormal(vec3 p) {
  vec2 e = vec2(0.001, 0.0);
  return normalize(vec3(
    map(p + e.xyy) - map(p - e.xyy),
    map(p + e.yxy) - map(p - e.yxy),
    map(p + e.yyx) - map(p - e.yyx)
  ));
}
```

### Lighting & Shading

```glsl
// Soft shadows
float softShadow(vec3 ro, vec3 rd, float mint, float maxt, float k) {
  float res = 1.0;
  float t = mint;
  for(int i = 0; i < 16; i++) {
    float h = map(ro + rd * t);
    res = min(res, k * h / t);
    t += clamp(h, 0.02, 0.10);
    if(res < 0.001 || t > maxt) break;
  }
  return clamp(res, 0.0, 1.0);
}

// Ambient occlusion
float calcAO(vec3 p, vec3 n) {
  float occ = 0.0;
  float sca = 1.0;
  for(int i = 0; i < 5; i++) {
    float h = 0.01 + 0.12 * float(i) / 4.0;
    float d = map(p + h * n);
    occ += (h - d) * sca;
    sca *= 0.95;
  }
  return clamp(1.0 - 3.0 * occ, 0.0, 1.0);
}

// PBR
vec3 pbr(vec3 albedo, float metallic, float roughness, vec3 n, vec3 v, vec3 l) {
  vec3 h = normalize(v + l);
  float NdotL = max(dot(n, l), 0.0);
  float NdotV = max(dot(n, v), 0.0);
  float NdotH = max(dot(n, h), 0.0);
  float HdotV = max(dot(h, v), 0.0);

  vec3 F0 = mix(vec3(0.04), albedo, metallic);
  vec3 F = F0 + (1.0 - F0) * pow(1.0 - HdotV, 5.0);

  // Add lighting calculation
  return F * NdotL;
}
```

### Noise & Procedural Generation

```glsl
// Value noise
float hash(float n) { return fract(sin(n) * 43758.5453); }

float noise(vec3 x) {
  vec3 p = floor(x);
  vec3 f = fract(x);
  f = f * f * (3.0 - 2.0 * f);
  float n = p.x + p.y * 57.0 + 113.0 * p.z;
  return mix(
    mix(mix(hash(n), hash(n + 1.0), f.x),
        mix(hash(n + 57.0), hash(n + 58.0), f.x), f.y),
    mix(mix(hash(n + 113.0), hash(n + 114.0), f.x),
        mix(hash(n + 170.0), hash(n + 171.0), f.x), f.y), f.z);
}

// FBM (Fractal Brownian Motion)
float fbm(vec3 p) {
  float value = 0.0;
  float amplitude = 0.5;
  float frequency = 1.0;
  for(int i = 0; i < 6; i++) {
    value += amplitude * noise(p * frequency);
    amplitude *= 0.5;
    frequency *= 2.0;
  }
  return value;
}

// Voronoi
vec2 voronoi(vec2 p) {
  vec2 n = floor(p);
  vec2 f = fract(p);
  float md = 8.0;
  vec2 mr;
  for(int j = -1; j <= 1; j++) {
    for(int i = -1; i <= 1; i++) {
      vec2 g = vec2(float(i), float(j));
      vec2 o = vec2(hash(n.x + g.x + n.y + g.y * 57.0));
      vec2 r = g + o - f;
      float d = dot(r, r);
      if(d < md) { md = d; mr = r; }
    }
  }
  return vec2(sqrt(md), mr);
}
```

### Post-Processing

```glsl
// ACES Tone Mapping
vec3 aces(vec3 x) {
  float a = 2.51;
  float b = 0.03;
  float c = 2.43;
  float d = 0.59;
  float e = 0.14;
  return clamp((x * (a * x + b)) / (x * (c * x + d) + e), 0.0, 1.0);
}

// Bloom
vec3 bloom(vec2 uv, sampler2D tex) {
  vec3 col = texture(tex, uv).rgb;
  vec3 bloom = vec3(0.0);
  for(int i = 0; i < 8; i++) {
    float t = float(i) / 8.0;
    bloom += texture(tex, uv + vec2(t * 0.01)).rgb;
  }
  bloom /= 8.0;
  return col + bloom * 0.5;
}

// Chromatic Aberration
vec3 chromaticAberration(vec2 uv, sampler2D tex) {
  vec2 center = vec2(0.5);
  vec2 dir = uv - center;
  float dist = length(dir);
  float offset = dist * 0.02;
  return vec3(
    texture(tex, uv + dir * offset).r,
    texture(tex, uv).g,
    texture(tex, uv - dir * offset).b
  );
}
```

## WebGL2 Adaptation Rules

```glsl
#version 300 es
precision highp float;

out vec4 fragColor;  // ✅ Required

void main() {
  // Wrap ShaderToy mainImage
  mainImage(fragColor, gl_FragCoord.xy);
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
  // Your shader code here
}
```

## Performance Limits

```
✅ MAX_STEPS: ≤ 128 ray march steps
✅ Volume steps: ≤ 32
✅ FBM octaves: ≤ 6
❌ Avoid nested loops
❌ Avoid dynamic branching in hot paths
```

## Debug Techniques

```glsl
// Normal visualization
col = nor * 0.5 + 0.5;

// Step count heatmap
col = vec3(float(steps) / float(MAX_STEPS));

// SDF color bands
col = vec3(sin(d * 100.0) * 0.5 + 0.5);

// UV checker
vec2 uv = fragCoord / resolution.xy;
col = vec3(mod(floor(uv.x * 10.0) + floor(uv.y * 10.0), 2.0) * 0.5);
```

## Integration with 天龙引擎

**Upgrades:**
- 13-01 设计师 V10.2 → V10.3: Shader/3D graphics
- 10-03 算法工程师 V1.0: GPU programming

**Synergies:**
- algorithmic-art: Procedural art patterns
- canvas-design: WebGL canvas
- remotion-best-practices: Video shader effects
