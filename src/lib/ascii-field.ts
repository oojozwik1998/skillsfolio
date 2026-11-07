/**
 * Animated field of random characters behind the home page hero.
 * Browser APIs come in through `FieldHost`, so the whole thing runs in unit tests.
 */

export const fieldChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

export interface FieldConfig {
  /** Cell size in CSS pixels. */
  cellWidth: number;
  cellHeight: number;
  fontSize: number;
  /** Share of characters swapped on every frame, 0 to 1. */
  swapRate: number;
  framesPerSecond: number;
  /** Opacity of cells outside the bright patches. */
  baseAlpha: number;
  /** Extra opacity at the centre of a bright patch. */
  patchAlpha: number;
  /** Reach of the pointer spotlight in CSS pixels. */
  pointerRadius: number;
  /** Extra opacity right under the pointer. */
  pointerAlpha: number;
  /** Chance per frame that a character under the pointer is swapped. */
  pointerSwapRate: number;
}

export const defaultFieldConfig: FieldConfig = {
  cellWidth: 6,
  cellHeight: 12,
  fontSize: 9,
  swapRate: 0.02,
  framesPerSecond: 20,
  baseAlpha: 0.035,
  patchAlpha: 0.24,
  pointerRadius: 240,
  pointerAlpha: 0.35,
  pointerSwapRate: 0.25,
};

export interface Point {
  x: number;
  y: number;
}

export type Random = () => number;

export interface Field {
  cols: number;
  rows: number;
  cells: string[];
}

export function randomChar(random: Random): string {
  return fieldChars.charAt(Math.floor(random() * fieldChars.length) % fieldChars.length);
}

export function createField(width: number, height: number, config: FieldConfig, random: Random): Field {
  const cols = Math.max(0, Math.ceil(width / config.cellWidth));
  const rows = Math.max(0, Math.ceil(height / config.cellHeight));
  const cells = Array.from({ length: cols * rows }, () => randomChar(random));
  return { cols, rows, cells };
}

/** Replaces a random share of characters, so the field flickers. */
export function swapChars(field: Field, rate: number, random: Random): void {
  const count = Math.round(field.cells.length * rate);
  for (let i = 0; i < count; i += 1) {
    const index = Math.floor(random() * field.cells.length) % field.cells.length;
    field.cells[index] = randomChar(random);
  }
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

const glowFalloff = 4;
const glowFloor = Math.exp(-glowFalloff);

/**
 * Soft glow around the pointer: 1 right under it, fading like a blur to exactly 0
 * at the edge of the radius, so the glow has no visible rim.
 */
export function pointerStrength(x: number, y: number, pointer: Point | null, radius: number): number {
  if (!pointer) return 0;
  const distance = Math.min(1, Math.hypot(x - pointer.x, y - pointer.y) / radius);
  return (Math.exp(-glowFalloff * distance * distance) - glowFloor) / (1 - glowFloor);
}

/** Centre of a cell in CSS pixels. */
function cellCentre(index: number, field: Field, config: FieldConfig): Point {
  return {
    x: ((index % field.cols) + 0.5) * config.cellWidth,
    y: (Math.floor(index / field.cols) + 0.5) * config.cellHeight,
  };
}

/** Swaps characters near the pointer more often, fading with the glow, so the field reacts to hover. */
export function scrambleNear(field: Field, pointer: Point | null, config: FieldConfig, random: Random): void {
  if (!pointer) return;
  field.cells.forEach((_, index) => {
    const { x, y } = cellCentre(index, field, config);
    const strength = pointerStrength(x, y, pointer, config.pointerRadius);
    if (strength > 0 && random() < config.pointerSwapRate * strength) {
      field.cells[index] = randomChar(random);
    }
  });
}

export type DrawTarget = Pick<
  CanvasRenderingContext2D,
  'globalAlpha' | 'fillStyle' | 'font' | 'textBaseline' | 'clearRect' | 'fillText' | 'setTransform'
>;

export interface DrawStyle {
  color: string;
  fontFamily: string;
  width: number;
  height: number;
  pointer: Point | null;
}

export function drawField(
  context: DrawTarget,
  field: Field,
  seconds: number,
  config: FieldConfig,
  style: DrawStyle,
): void {
  context.clearRect(0, 0, style.width, style.height);
  context.fillStyle = style.color;
  context.font = `${config.fontSize}px ${style.fontFamily}`;
  context.textBaseline = 'top';

  field.cells.forEach((char, index) => {
    const col = index % field.cols;
    const row = Math.floor(index / field.cols);
    const { x, y } = cellCentre(index, field, config);
    context.globalAlpha = Math.min(
      1,
      config.baseAlpha +
        config.patchAlpha * patchStrength(x, y, seconds) +
        config.pointerAlpha * pointerStrength(x, y, style.pointer, config.pointerRadius),
    );
    context.fillText(char, col * config.cellWidth, row * config.cellHeight);
  });
  context.globalAlpha = 1;
}

export interface FieldHost {
  context: DrawTarget;
  /** Size of the canvas element in CSS pixels and the device pixel ratio. */
  measure(): { width: number; height: number; pixelRatio: number };
  /** Sets the canvas bitmap size in device pixels. */
  setBitmapSize(width: number, height: number): void;
  color(): string;
  fontFamily(): string;
  requestFrame(callback: (milliseconds: number) => void): number;
  cancelFrame(id: number): void;
  random: Random;
  reducedMotion: boolean;
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

export function createFieldAnimation(host: FieldHost, config: FieldConfig = defaultFieldConfig): FieldAnimation {
  let field: Field = { cols: 0, rows: 0, cells: [] };
  let size = { width: 0, height: 0 };
  let frameId: number | undefined;
  let lastDraw = 0;
  let seconds = 0;
  let pointer: Point | null = null;
  const frameInterval = 1000 / config.framesPerSecond;

  const draw = () => {
    drawField(host.context, field, seconds, config, {
      color: host.color(),
      fontFamily: host.fontFamily(),
      ...size,
      pointer,
    });
  };

  const tick = (milliseconds: number) => {
    frameId = host.requestFrame(tick);
    if (milliseconds - lastDraw < frameInterval) return;
    lastDraw = milliseconds;
    seconds = milliseconds / 1000;
    swapChars(field, config.swapRate, host.random);
    scrambleNear(field, pointer, config, host.random);
    draw();
  };

  const stop = () => {
    if (frameId === undefined) return;
    host.cancelFrame(frameId);
    frameId = undefined;
  };

  return {
    resize() {
      const { width, height, pixelRatio } = host.measure();
      size = { width, height };
      host.setBitmapSize(Math.round(width * pixelRatio), Math.round(height * pixelRatio));
      host.context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
      field = createField(width, height, config, host.random);
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
