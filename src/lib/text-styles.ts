/**
 * Reads text style rules from CSS so the hand-written `type-*` utilities can be
 * compared with the generated design-system text styles (`.ds-text-*`).
 */

export type TextStyle = Record<string, string>;

const FONT_ALIASES: Record<string, string> = {
  'var(--font-display)': 'var(--ds-font-family-display)',
  'var(--font-body)': 'var(--ds-font-family-body)',
  'var(--font-mono)': 'var(--ds-font-family-code)',
};

const DEFAULTS: TextStyle = { 'letter-spacing': '0em' };

function normalize(declarations: string): TextStyle {
  const style: TextStyle = { ...DEFAULTS };
  for (const line of declarations.split(';')) {
    const colon = line.indexOf(':');
    if (colon === -1) continue;
    const property = line.slice(0, colon).trim();
    const value = line.slice(colon + 1).trim();
    style[property] = FONT_ALIASES[value] ?? value;
  }
  return style;
}

/** Text styles declared as `@utility type-<name> { ... }`. */
export function utilityTextStyles(css: string): Record<string, TextStyle> {
  return collect(css, /@utility type-([a-z-]+)\s*\{([^}]*)\}/g);
}

/** Text styles declared as `.ds-text-<name> { ... }`. */
export function generatedTextStyles(css: string): Record<string, TextStyle> {
  return collect(css, /\.ds-text-([a-z-]+)\s*\{([^}]*)\}/g);
}

function collect(css: string, pattern: RegExp): Record<string, TextStyle> {
  const styles: Record<string, TextStyle> = {};
  for (const [, name = '', body = ''] of css.matchAll(pattern)) {
    styles[name] = normalize(body);
  }
  return styles;
}
