/**
 * Animated field behind the home page hero: large letters drawn from dots. Letters
 * keep changing, faint wave shapes drift through them, and dots scatter away from
 * the mouse and spring back. Browser APIs come in through `FieldHost`, so the whole
 * thing runs in unit tests.
 */

export type Random = () => number;

export interface Point {
  x: number;
  y: number;
}

/** 0 below `edge0`, 1 above `edge1`, with an S-curve in between, so shapes fade in softly. */
function smoothstep(edge0: number, edge1: number, value: number): number {
  const t = Math.min(1, Math.max(0, (value - edge0) / (edge1 - edge0)));
  return t * t * (3 - 2 * t);
}

/**
 * Large drifting wave shapes, in CSS pixels: 0 outside a shape, up to 1 inside.
 * The coordinates are bent by slow sine waves, so straight bands turn into
 * flowing ribbons, and a large slow blob makes them swell and fade.
 */
export function patchStrength(x: number, y: number, seconds: number): number {
  const bentX = x + 90 * Math.sin(y * 0.006 + seconds * 0.3);
  const bentY = y + 90 * Math.sin(x * 0.005 - seconds * 0.25);
  const ribbon = Math.sin(bentX * 0.006 + 2.2 * Math.sin(bentY * 0.008 + seconds * 0.35) + seconds * 0.4);
  const swell = (Math.sin(x * 0.003 + seconds * 0.15) + Math.sin(y * 0.004 - seconds * 0.12)) / 2;
  return smoothstep(0.15, 0.95, ribbon * 0.6 + swell * 0.4);
}

export interface FieldAnimation {
  /** Rebuilds the grid for the current size and draws a frame. */
  resize(): void;
  /** Starts or pauses the loop, for example when the hero leaves the screen. */
  setActive(active: boolean): void;
  /** Pointer position relative to the canvas in CSS pixels, or null when it leaves. Ignored with reduced motion. */
  setPointer(pointer: Point | null): void;
  /** Draws the current frame again, for example after a color scheme change. */
  redraw(): void;
  destroy(): void;
}
/** 5 × 7 dot matrix, one string per row, `#` is a dot. */
export const glyphs: Record<string, readonly string[]> = {
  A: ['.###.', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'],
  B: ['####.', '#...#', '#...#', '####.', '#...#', '#...#', '####.'],
  C: ['.###.', '#...#', '#....', '#....', '#....', '#...#', '.###.'],
  D: ['###..', '#..#.', '#...#', '#...#', '#...#', '#..#.', '###..'],
  E: ['#####', '#....', '#....', '####.', '#....', '#....', '#####'],
  F: ['#####', '#....', '#....', '####.', '#....', '#....', '#....'],
  G: ['.###.', '#...#', '#....', '#.###', '#...#', '#...#', '.####'],
  H: ['#...#', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'],
  I: ['.###.', '..#..', '..#..', '..#..', '..#..', '..#..', '.###.'],
  J: ['..###', '...#.', '...#.', '...#.', '...#.', '#..#.', '.##..'],
  K: ['#...#', '#..#.', '#.#..', '##...', '#.#..', '#..#.', '#...#'],
  L: ['#....', '#....', '#....', '#....', '#....', '#....', '#####'],
  M: ['#...#', '##.##', '#.#.#', '#.#.#', '#...#', '#...#', '#...#'],
  N: ['#...#', '#...#', '##..#', '#.#.#', '#..##', '#...#', '#...#'],
  O: ['.###.', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'],
  P: ['####.', '#...#', '#...#', '####.', '#....', '#....', '#....'],
  Q: ['.###.', '#...#', '#...#', '#...#', '#.#.#', '#..#.', '.##.#'],
  R: ['####.', '#...#', '#...#', '####.', '#.#..', '#..#.', '#...#'],
  S: ['.####', '#....', '#....', '.###.', '....#', '....#', '####.'],
  T: ['#####', '..#..', '..#..', '..#..', '..#..', '..#..', '..#..'],
  U: ['#...#', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'],
  V: ['#...#', '#...#', '#...#', '#...#', '#...#', '.#.#.', '..#..'],
  W: ['#...#', '#...#', '#...#', '#.#.#', '#.#.#', '#.#.#', '.#.#.'],
  X: ['#...#', '#...#', '.#.#.', '..#..', '.#.#.', '#...#', '#...#'],
  Y: ['#...#', '#...#', '.#.#.', '..#..', '..#..', '..#..', '..#..'],
  Z: ['#####', '....#', '...#.', '..#..', '.#...', '#....', '#####'],
  '0': ['.###.', '#...#', '#..##', '#.#.#', '##..#', '#...#', '.###.'],
  '1': ['..#..', '.##..', '..#..', '..#..', '..#..', '..#..', '.###.'],
  '2': ['.###.', '#...#', '....#', '...#.', '..#..', '.#...', '#####'],
  '3': ['#####', '...#.', '..#..', '...#.', '....#', '#...#', '.###.'],
  '4': ['...#.', '..##.', '.#.#.', '#..#.', '#####', '...#.', '...#.'],
  '5': ['#####', '#....', '####.', '....#', '....#', '#...#', '.###.'],
  '6': ['..##.', '.#...', '#....', '####.', '#...#', '#...#', '.###.'],
  '7': ['#####', '....#', '...#.', '..#..', '.#...', '.#...', '.#...'],
  '8': ['.###.', '#...#', '#...#', '.###.', '#...#', '#...#', '.###.'],
  '9': ['.###.', '#...#', '#...#', '.####', '....#', '...#.', '.##..'],
};

export const glyphChars = Object.keys(glyphs);
export const glyphColumns = 5;
export const glyphRows = 7;
export const dotsPerLetter = glyphColumns * glyphRows;

/** Dots of a glyph in reading order: true where the glyph has a dot. */
export function glyphDots(char: string): boolean[] {
  return (glyphs[char] ?? []).join('').split('').map((cell) => cell === '#');
}

export interface DotFieldConfig {
  /** Distance between dot centres in CSS pixels. */
  dotPitch: number;
  dotSize: number;
  /** Space between letters in CSS pixels. */
  letterGapX: number;
  letterGapY: number;
  /** Share of letters that change per second. */
  swapRate: number;
  /** Share of the way a dot fades to its new state each frame. */
  fadeSpeed: number;
  baseAlpha: number;
  patchAlpha: number;
  /** Extra opacity for dots pushed out of place, at full displacement. */
  scatterAlpha: number;
  /** Displacement in CSS pixels that counts as full. */
  scatterDistance: number;
  pointerRadius: number;
  /** Push per frame right under the pointer, in CSS pixels. */
  pushStrength: number;
  /** How far each dot's flight bends away from straight out, in radians either way. */
  scatterSpread: number;
  /** Random kick per frame right under the pointer, in CSS pixels. */
  scatterNoise: number;
  /** Pull back to the home position per frame, as a share of the distance. */
  spring: number;
  /** Share of velocity kept each frame. */
  damping: number;
}

export const defaultDotFieldConfig: DotFieldConfig = {
  dotPitch: 5,
  dotSize: 2,
  letterGapX: 12,
  letterGapY: 16,
  swapRate: 0.4,
  fadeSpeed: 0.25,
  baseAlpha: 0.05,
  patchAlpha: 0.55,
  scatterAlpha: 0.35,
  scatterDistance: 60,
  pointerRadius: 200,
  pushStrength: 1.6,
  scatterSpread: 1.3,
  scatterNoise: 0.6,
  spring: 0.02,
  damping: 0.9,
};

export interface DotField {
  cols: number;
  rows: number;
  homeX: Float32Array;
  homeY: Float32Array;
  x: Float32Array;
  y: Float32Array;
  vx: Float32Array;
  vy: Float32Array;
  /** Current visibility of each dot, 0 to 1. */
  level: Float32Array;
  /** Target visibility of each dot: 1 when the letter has a dot there. */
  target: Uint8Array;
}

function letterSize(config: DotFieldConfig) {
  return {
    width: glyphColumns * config.dotPitch + config.letterGapX,
    height: glyphRows * config.dotPitch + config.letterGapY,
  };
}

export function setLetter(field: DotField, letter: number, char: string): void {
  glyphDots(char).forEach((on, dot) => {
    field.target[letter * dotsPerLetter + dot] = on ? 1 : 0;
  });
}

function randomGlyph(random: Random): string {
  return glyphChars[Math.floor(random() * glyphChars.length) % glyphChars.length];
}

export function createDotField(width: number, height: number, config: DotFieldConfig, random: Random): DotField {
  const size = letterSize(config);
  const cols = Math.max(0, Math.ceil(width / size.width));
  const rows = Math.max(0, Math.ceil(height / size.height));
  const count = cols * rows * dotsPerLetter;
  const field: DotField = {
    cols,
    rows,
    homeX: new Float32Array(count),
    homeY: new Float32Array(count),
    x: new Float32Array(count),
    y: new Float32Array(count),
    vx: new Float32Array(count),
    vy: new Float32Array(count),
    level: new Float32Array(count),
    target: new Uint8Array(count),
  };

  for (let letter = 0; letter < cols * rows; letter += 1) {
    const left = (letter % cols) * size.width + config.letterGapX / 2;
    const top = Math.floor(letter / cols) * size.height + config.letterGapY / 2;
    for (let dot = 0; dot < dotsPerLetter; dot += 1) {
      const i = letter * dotsPerLetter + dot;
      field.homeX[i] = field.x[i] = left + ((dot % glyphColumns) + 0.5) * config.dotPitch;
      field.homeY[i] = field.y[i] = top + (Math.floor(dot / glyphColumns) + 0.5) * config.dotPitch;
    }
    setLetter(field, letter, randomGlyph(random));
  }
  field.level.set(field.target);
  return field;
}

/** Changes a random share of letters; `seconds` is the time since the last call. */
export function swapLetters(field: DotField, rate: number, seconds: number, random: Random): void {
  const letters = field.cols * field.rows;
  const count = Math.floor(letters * rate * seconds + random());
  for (let n = 0; n < count; n += 1) {
    setLetter(field, Math.floor(random() * letters) % letters, randomGlyph(random));
  }
}

/** Fixed per-dot strength between 0.6 and 1.4, so letters break apart unevenly. */
export function dotJitter(index: number): number {
  const noise = Math.sin(index * 12.9898) * 43758.5453;
  return 0.6 + 0.8 * (noise - Math.floor(noise));
}

/**
 * One frame: fade dots, scatter them away from the pointer and spring them back.
 * Each dot flies out at its own angle and gets a random kick, so letters burst apart.
 */
export function stepDots(field: DotField, pointer: Point | null, config: DotFieldConfig, random: Random): void {
  for (let i = 0; i < field.level.length; i += 1) {
    const target = field.target[i];
    const level = field.level[i];
    field.level[i] = level + (target - level) * config.fadeSpeed;

    let x = field.x[i];
    let y = field.y[i];
    let vx = field.vx[i];
    let vy = field.vy[i];

    if (pointer) {
      const dx = x - pointer.x;
      const dy = y - pointer.y;
      const distance = Math.hypot(dx, dy);
      if (distance < config.pointerRadius) {
        const reach = 1 - distance / config.pointerRadius;
        const strength = reach * reach;
        const push = (strength * config.pushStrength * dotJitter(i)) / (distance || 1);
        const bend = (dotJitter(i + 7919) - 1) * 2.5 * config.scatterSpread;
        const cos = Math.cos(bend);
        const sin = Math.sin(bend);
        vx += (dx * cos - dy * sin) * push + (random() * 2 - 1) * config.scatterNoise * strength;
        vy += (dx * sin + dy * cos) * push + (random() * 2 - 1) * config.scatterNoise * strength;
      }
    }

    vx = (vx + (field.homeX[i] - x) * config.spring) * config.damping;
    vy = (vy + (field.homeY[i] - y) * config.spring) * config.damping;
    x += vx;
    y += vy;

    field.x[i] = x;
    field.y[i] = y;
    field.vx[i] = vx;
    field.vy[i] = vy;
  }
}

export type DotDrawTarget = Pick<
  CanvasRenderingContext2D,
  'globalAlpha' | 'fillStyle' | 'clearRect' | 'fillRect' | 'setTransform'
>;

export interface DotDrawStyle {
  color: string;
  width: number;
  height: number;
}

export function drawDots(
  context: DotDrawTarget,
  field: DotField,
  seconds: number,
  config: DotFieldConfig,
  style: DotDrawStyle,
): void {
  context.clearRect(0, 0, style.width, style.height);
  context.fillStyle = style.color;
  const half = config.dotSize / 2;

  for (let letter = 0; letter < field.cols * field.rows; letter += 1) {
    const first = letter * dotsPerLetter;
    const wave = config.baseAlpha + config.patchAlpha * patchStrength(field.homeX[first], field.homeY[first], seconds);
    for (let i = first; i < first + dotsPerLetter; i += 1) {
      const level = field.level[i];
      if (level < 0.01) continue;
      const x = field.x[i];
      const y = field.y[i];
      const scatter = Math.min(1, Math.hypot(x - field.homeX[i], y - field.homeY[i]) / config.scatterDistance);
      context.globalAlpha = Math.min(1, level * (wave + config.scatterAlpha * scatter));
      context.fillRect(x - half, y - half, config.dotSize, config.dotSize);
    }
  }
  context.globalAlpha = 1;
}

export interface FieldHost {
  context: DotDrawTarget;
  /** Size of the canvas element in CSS pixels and the device pixel ratio. */
  measure(): { width: number; height: number; pixelRatio: number };
  /** Sets the canvas bitmap size in device pixels. */
  setBitmapSize(width: number, height: number): void;
  color(): string;
  requestFrame(callback: (milliseconds: number) => void): number;
  cancelFrame(id: number): void;
  random: Random;
  reducedMotion: boolean;
}

export function createDotFieldAnimation(
  host: FieldHost,
  config: DotFieldConfig = defaultDotFieldConfig,
): FieldAnimation {
  let field = createDotField(0, 0, config, host.random);
  let size = { width: 0, height: 0 };
  let frameId: number | undefined;
  let last: number | undefined;
  let seconds = 0;
  let pointer: Point | null = null;

  const draw = () => drawDots(host.context, field, seconds, config, { color: host.color(), ...size });

  const tick = (milliseconds: number) => {
    frameId = host.requestFrame(tick);
    const elapsed = Math.min(0.1, (milliseconds - (last ?? milliseconds)) / 1000);
    last = milliseconds;
    seconds = milliseconds / 1000;
    swapLetters(field, config.swapRate, elapsed, host.random);
    stepDots(field, pointer, config, host.random);
    draw();
  };

  const stop = () => {
    if (frameId === undefined) return;
    host.cancelFrame(frameId);
    frameId = undefined;
    last = undefined;
  };

  return {
    resize() {
      const { width, height, pixelRatio } = host.measure();
      size = { width, height };
      host.setBitmapSize(Math.round(width * pixelRatio), Math.round(height * pixelRatio));
      host.context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
      field = createDotField(width, height, config, host.random);
      draw();
    },
    setActive(active) {
      if (!active || host.reducedMotion) {
        stop();
        return;
      }
      if (frameId === undefined) frameId = host.requestFrame(tick);
    },
    setPointer(next) {
      if (!host.reducedMotion) pointer = next;
    },
    redraw: draw,
    destroy: stop,
  };
}
