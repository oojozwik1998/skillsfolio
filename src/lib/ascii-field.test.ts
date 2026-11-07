import { describe, expect, it, vi } from 'vitest';
import {
  createField,
  createFieldAnimation,
  defaultFieldConfig,
  type DrawTarget,
  drawField,
  type FieldHost,
  fieldChars,
  patchStrength,
  pointerStrength,
  scrambleNear,
  randomChar,
  swapChars,
} from './ascii-field';

const config = { ...defaultFieldConfig, cellWidth: 10, cellHeight: 10, pointerRadius: 10, pointerSwapRate: 0.5 };

function sequence(...values: number[]) {
  let i = 0;
  return () => values[i++ % values.length] ?? 0;
}

function fakeContext() {
  return {
    globalAlpha: 1,
    fillStyle: '',
    font: '',
    textBaseline: 'alphabetic',
    clearRect: vi.fn(),
    fillText: vi.fn(),
    setTransform: vi.fn(),
  } satisfies DrawTarget;
}

function fakeHost(overrides: Partial<FieldHost> = {}) {
  const frames: ((ms: number) => void)[] = [];
  const context = fakeContext();
  const host = {
    context,
    measure: () => ({ width: 30, height: 20, pixelRatio: 2 }),
    setBitmapSize: vi.fn(),
    color: () => 'gray',
    fontFamily: () => 'monospace',
    requestFrame: vi.fn((callback: (ms: number) => void) => frames.push(callback)),
    cancelFrame: vi.fn(),
    random: sequence(0.5),
    reducedMotion: false,
    ...overrides,
  } satisfies FieldHost;
  const runFrame = (ms: number) => frames.at(-1)?.(ms);
  return { host, context, runFrame };
}

describe('randomChar', () => {
  it('picks from the character set, including both ends', () => {
    expect(randomChar(() => 0)).toBe(fieldChars[0]);
    expect(randomChar(() => 0.9999)).toBe(fieldChars.at(-1));
    expect(randomChar(() => 1)).toBe(fieldChars[0]);
  });
});

describe('createField', () => {
  it('covers the area with whole cells', () => {
    const field = createField(25, 15, config, () => 0);
    expect(field).toMatchObject({ cols: 3, rows: 2 });
    expect(field.cells).toHaveLength(6);
  });

  it('is empty for an empty area', () => {
    expect(createField(0, 0, config, () => 0).cells).toEqual([]);
  });
});

describe('swapChars', () => {
  it('replaces the given share of cells', () => {
    const field = createField(100, 10, config, () => 0);
    swapChars(field, 0.2, sequence(0, 0.5, 0.5, 0.5));
    expect(field.cells.filter((char) => char !== fieldChars[0])).toHaveLength(2);
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

describe('pointerStrength', () => {
  it('is 1 under the pointer, fades softly to 0 at the edge and is 0 without a pointer', () => {
    expect(pointerStrength(5, 5, { x: 5, y: 5 }, 10)).toBe(1);
    expect(pointerStrength(10, 5, { x: 5, y: 5 }, 10)).toBeCloseTo(0.356, 3);
    expect(pointerStrength(14.9, 5, { x: 5, y: 5 }, 10)).toBeLessThan(0.002);
    expect(pointerStrength(50, 5, { x: 5, y: 5 }, 10)).toBe(0);
    expect(pointerStrength(5, 5, null, 10)).toBe(0);
  });
});

describe('scrambleNear', () => {
  it('swaps only characters within reach of the pointer, by chance', () => {
    const field = createField(40, 10, config, () => 0);
    scrambleNear(field, { x: 5, y: 5 }, config, sequence(0.1, 0.5));
    expect(field.cells.map((char) => char !== fieldChars[0])).toEqual([true, false, false, false]);
  });

  it('does nothing without a pointer', () => {
    const field = createField(40, 10, config, () => 0);
    scrambleNear(field, null, config, () => 0.1);
    expect(field.cells.every((char) => char === fieldChars[0])).toBe(true);
  });
});

describe('drawField', () => {
  it('brightens cells under the pointer, up to full opacity', () => {
    const context = fakeContext();
    const alphas: number[] = [];
    context.fillText.mockImplementation(() => alphas.push(context.globalAlpha));
    const field = createField(20, 10, config, () => 0);
    const bright = { ...config, pointerAlpha: 2 };
    drawField(context, field, 0, bright, { color: 'red', fontFamily: 'mono', width: 20, height: 10, pointer: { x: 5, y: 5 } });

    expect(alphas[0]).toBe(1);
    expect(alphas[1]).toBeLessThan(1);
  });

  it('clears the canvas and draws every cell in its place', () => {
    const context = fakeContext();
    const field = createField(20, 20, config, () => 0);
    drawField(context, field, 0, config, { color: 'red', fontFamily: 'mono', width: 20, height: 20, pointer: null });

    expect(context.clearRect).toHaveBeenCalledWith(0, 0, 20, 20);
    expect(context.fillStyle).toBe('red');
    expect(context.font).toBe(`${config.fontSize}px mono`);
    expect(context.textBaseline).toBe('top');
    expect(context.fillText.mock.calls.map(([, x, y]) => [x, y])).toEqual([
      [0, 0],
      [10, 0],
      [0, 10],
      [10, 10],
    ]);
    expect(context.globalAlpha).toBe(1);
  });
});

describe('createFieldAnimation', () => {
  it('sizes the bitmap for the pixel ratio and draws on resize', () => {
    const { host, context } = fakeHost();
    createFieldAnimation(host, config).resize();

    expect(host.setBitmapSize).toHaveBeenCalledWith(60, 40);
    expect(context.setTransform).toHaveBeenCalledWith(2, 0, 0, 2, 0, 0);
    expect(context.fillText).toHaveBeenCalledTimes(6);
  });

  it('draws at the configured frame rate while active', () => {
    const { host, context, runFrame } = fakeHost();
    const animation = createFieldAnimation(host, config);
    animation.resize();
    animation.setActive(true);
    animation.setActive(true);
    expect(host.requestFrame).toHaveBeenCalledTimes(1);

    context.fillText.mockClear();
    runFrame(10);
    expect(context.fillText).not.toHaveBeenCalled();
    runFrame(100);
    expect(context.fillText).toHaveBeenCalledTimes(6);
  });

  it('pauses, and pausing twice is harmless', () => {
    const { host } = fakeHost();
    const animation = createFieldAnimation(host, config);
    animation.setActive(true);
    animation.setActive(false);
    animation.destroy();
    expect(host.cancelFrame).toHaveBeenCalledTimes(1);
  });

  it('follows the pointer while animating', () => {
    const { host, context, runFrame } = fakeHost({ random: () => 0.9 });
    const animation = createFieldAnimation(host, { ...config, pointerAlpha: 0 });
    animation.resize();
    animation.setActive(true);
    animation.setPointer({ x: 5, y: 5 });
    const alphas: number[] = [];
    context.fillText.mockImplementation(() => alphas.push(context.globalAlpha));
    runFrame(100);
    expect(alphas).toHaveLength(6);
  });

  it('never animates with reduced motion, but redraws on request', () => {
    const { host, context } = fakeHost({ reducedMotion: true });
    const animation = createFieldAnimation(host, config);
    animation.resize();
    animation.setActive(true);
    animation.setPointer({ x: 5, y: 5 });
    expect(host.requestFrame).not.toHaveBeenCalled();

    context.clearRect.mockClear();
    animation.redraw();
    expect(context.clearRect).toHaveBeenCalledTimes(1);
  });
});
