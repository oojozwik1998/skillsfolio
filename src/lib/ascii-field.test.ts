import { describe, expect, it, vi } from 'vitest';
import {
  createDotField,
  createDotFieldAnimation,
  defaultDotFieldConfig,
  type DotDrawTarget,
  type FieldHost,
  dotJitter,
  dotsPerLetter,
  drawDots,
  glyphChars,
  glyphColumns,
  glyphDots,
  glyphRows,
  glyphs,
  patchStrength,
  setLetter,
  stepDots,
  swapLetters,
} from './ascii-field';

// One letter is 5 × 5 + 5 = 30 wide and 7 × 5 + 5 = 40 high.
const config = { ...defaultDotFieldConfig, dotPitch: 5, letterGapX: 5, letterGapY: 5 };

function fakeContext() {
  return {
    globalAlpha: 1,
    fillStyle: '',
    clearRect: vi.fn(),
    fillRect: vi.fn(),
    setTransform: vi.fn(),
  } satisfies DotDrawTarget;
}

function fakeHost(overrides: Partial<FieldHost> = {}) {
  const frames: ((ms: number) => void)[] = [];
  const context = fakeContext();
  const host = {
    context,
    measure: () => ({ width: 60, height: 40, pixelRatio: 2 }),
    setBitmapSize: vi.fn(),
    color: () => 'gray',
    requestFrame: vi.fn((callback: (ms: number) => void) => frames.push(callback)),
    cancelFrame: vi.fn(),
    random: () => 0,
    reducedMotion: false,
    ...overrides,
  } satisfies FieldHost;
  const runFrame = (ms: number) => frames.at(-1)?.(ms);
  return { host, context, runFrame };
}

// Digits come first in key order, so random() = 0 picks '0' and 0.99 picks 'Z'.
const first = glyphChars[0] ?? '';
const last = glyphChars.at(-1) ?? '';
const dotCount = (char: string) => glyphDots(char).filter(Boolean).length;

describe('glyphs', () => {
  it('has a full 5 × 7 matrix with at least one dot for every character', () => {
    expect(glyphChars).toHaveLength(36);
    for (const char of glyphChars) {
      const rows = glyphs[char] ?? [];
      expect(rows).toHaveLength(glyphRows);
      for (const row of rows) expect(row).toMatch(new RegExp(`^[#.]{${glyphColumns}}$`));
      expect(dotCount(char)).toBeGreaterThan(0);
    }
  });

  it('has no dots for an unknown character', () => {
    expect(glyphDots('?')).toEqual([]);
  });
});

describe('createDotField', () => {
  it('lays out whole letters and places every dot at home and visible as its glyph', () => {
    const field = createDotField(50, 30, config, () => 0);
    expect(field).toMatchObject({ cols: 2, rows: 1 });
    expect(field.x).toHaveLength(2 * dotsPerLetter);
    expect([field.homeX[0], field.homeY[0]]).toEqual([5, 5]);
    expect(field.homeX[dotsPerLetter]).toBe(35);
    expect(field.x).toEqual(field.homeX);
    expect(Array.from(field.level)).toEqual(Array.from(field.target));
    expect(Array.from(field.target.slice(0, dotsPerLetter))).toEqual(glyphDots(first).map(Number));
  });

  it('is empty for an empty area', () => {
    expect(createDotField(0, 0, config, () => 0).x).toHaveLength(0);
  });
});

describe('setLetter and swapLetters', () => {
  it('sets the target dots of one letter', () => {
    const field = createDotField(30, 40, config, () => 0);
    setLetter(field, 0, 'I');
    expect(field.target.reduce((sum, on) => sum + on, 0)).toBe(dotCount('I'));
  });

  it('changes about rate × letters × seconds letters', () => {
    const field = createDotField(300, 40, config, () => 0);
    const random = vi.fn().mockReturnValueOnce(0).mockReturnValue(0.99);
    swapLetters(field, 0.2, 1, random);
    // 10 letters × 0.2 = 2 swaps, both to the last glyph in the last letter.
    expect(random).toHaveBeenCalledTimes(5);
    expect(field.target.slice(9 * dotsPerLetter).reduce((sum, on) => sum + on, 0)).toBe(dotCount(last));
  });
});

describe('dotJitter', () => {
  it('stays between 0.6 and 1.4 and differs between dots', () => {
    const values = Array.from({ length: 200 }, (_, i) => dotJitter(i));
    expect(Math.min(...values)).toBeGreaterThanOrEqual(0.6);
    expect(Math.max(...values)).toBeLessThanOrEqual(1.4);
    expect(new Set(values).size).toBeGreaterThan(150);
  });
});

describe('stepDots', () => {
  it('fades dots toward their target', () => {
    const field = createDotField(30, 40, config, () => 0);
    field.level.fill(0);
    stepDots(field, null, config, () => 0.5);
    expect(field.level[1]).toBeCloseTo(config.fadeSpeed);
    expect(field.level[0]).toBe(0);
  });

  it('pushes dots near the pointer away and leaves far dots in place', () => {
    const field = createDotField(300, 40, config, () => 0);
    const near = 1;
    stepDots(field, { x: field.homeX[near] - 3, y: field.homeY[near] }, config, () => 0.5);
    expect(field.x[near]).toBeGreaterThan(field.homeX[near]);
    const far = 9 * dotsPerLetter;
    expect(field.x[far]).toBe(field.homeX[far]);
  });

  it('sends dots out at different angles and adds a random kick', () => {
    const calm = createDotField(30, 40, config, () => 0);
    const kicked = createDotField(30, 40, config, () => 0);
    const pointer = { x: calm.homeX[0] - 3, y: calm.homeY[0] };
    stepDots(calm, pointer, config, () => 0.5);
    stepDots(kicked, pointer, config, () => 1);
    // Straight out from the pointer would keep y at home; the bend moves it.
    expect(calm.y[0]).not.toBeCloseTo(calm.homeY[0], 3);
    expect(kicked.x[0]).not.toBeCloseTo(calm.x[0], 3);
  });

  it('pushes a dot right under the pointer without dividing by zero', () => {
    const field = createDotField(30, 40, config, () => 0);
    stepDots(field, { x: field.homeX[0], y: field.homeY[0] }, config, () => 0.5);
    expect(Number.isFinite(field.x[0])).toBe(true);
  });

  it('springs scattered dots back home once the pointer leaves', () => {
    const field = createDotField(30, 40, config, () => 0);
    field.x[0] = field.homeX[0] + 30;
    for (let frame = 0; frame < 200; frame += 1) stepDots(field, null, config, () => 0.5);
    expect(field.x[0]).toBeCloseTo(field.homeX[0], 1);
  });
});

describe('drawDots', () => {
  it('draws only visible dots and brightens scattered ones, up to full opacity', () => {
    const context = fakeContext();
    const alphas: number[] = [];
    context.fillRect.mockImplementation(() => alphas.push(context.globalAlpha));
    const field = createDotField(30, 40, config, () => 0);
    drawDots(context, field, 0, config, { color: 'red', width: 30, height: 40 });

    expect(context.clearRect).toHaveBeenCalledWith(0, 0, 30, 40);
    expect(context.fillStyle).toBe('red');
    expect(context.fillRect).toHaveBeenCalledTimes(dotCount(first));
    expect(context.fillRect).toHaveBeenCalledWith(field.homeX[1] - 1, field.homeY[1] - 1, 2, 2);

    alphas.length = 0;
    field.x[1] += 100;
    drawDots(context, field, 0, { ...config, scatterAlpha: 5 }, { color: 'red', width: 30, height: 40 });
    expect(alphas[0]).toBe(1);
    expect(alphas[1]).toBeLessThan(1);
    expect(context.globalAlpha).toBe(1);
  });
});

describe('createDotFieldAnimation', () => {
  it('sizes the bitmap for the pixel ratio and draws on resize', () => {
    const { host, context } = fakeHost();
    createDotFieldAnimation(host, config).resize();
    expect(host.setBitmapSize).toHaveBeenCalledWith(120, 80);
    expect(context.setTransform).toHaveBeenCalledWith(2, 0, 0, 2, 0, 0);
    expect(context.fillRect).toHaveBeenCalledTimes(2 * dotCount(first));
  });

  it('animates every frame and scatters dots around the pointer', () => {
    const { host, context, runFrame } = fakeHost();
    const animation = createDotFieldAnimation(host, config);
    animation.resize();
    animation.setActive(true);
    animation.setActive(true);
    expect(host.requestFrame).toHaveBeenCalledTimes(1);

    animation.setPointer({ x: 3, y: 5 });
    context.fillRect.mockClear();
    runFrame(16);
    runFrame(32);
    expect(context.fillRect).toHaveBeenCalledTimes(4 * dotCount(first));
    const [x = 0, y = 0] = context.fillRect.mock.calls.at(-2 * dotCount(first)) ?? [];
    // The first visible dot rests at (9, 4) once the half dot size is taken off.
    expect(Math.hypot(x - 9, y - 4)).toBeGreaterThan(0.5);
  });

  it('pauses, restarts the clock, and pausing twice is harmless', () => {
    const { host } = fakeHost();
    const animation = createDotFieldAnimation(host, config);
    animation.setActive(true);
    animation.setActive(false);
    animation.destroy();
    expect(host.cancelFrame).toHaveBeenCalledTimes(1);
  });

  it('never animates or reacts to the pointer with reduced motion, but redraws on request', () => {
    const { host, context } = fakeHost({ reducedMotion: true });
    const animation = createDotFieldAnimation(host, config);
    animation.resize();
    animation.setActive(true);
    animation.setPointer({ x: 3, y: 5 });
    expect(host.requestFrame).not.toHaveBeenCalled();

    context.clearRect.mockClear();
    animation.redraw();
    expect(context.clearRect).toHaveBeenCalledTimes(1);
  });
});

describe('patchStrength', () => {
  it('stays between 0 and 1 and is 0 in places', () => {
    const values = Array.from({ length: 400 }, (_, i) => patchStrength((i % 40) * 30, Math.floor(i / 40) * 60, 3));
    expect(Math.min(...values)).toBe(0);
    expect(Math.max(...values)).toBeLessThanOrEqual(1);
    expect(Math.max(...values)).toBeGreaterThan(0);
  });
});
