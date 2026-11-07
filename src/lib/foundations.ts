/** Groups design tokens for the foundations documentation in Storybook. */

export interface TokenEntry {
  id: string;
  cssVar: string;
}

/** Tokens whose id starts with one of the prefixes, in the given order. */
export function tokensByPrefix(tokens: Record<string, string>, prefixes: readonly string[]): TokenEntry[] {
  return Object.entries(tokens)
    .filter(([id]) => prefixes.some((prefix) => id.startsWith(`${prefix}.`)))
    .map(([id, cssVar]) => ({ id, cssVar }));
}

/** Numeric scale tokens (for example `space.4`) sorted from smallest to largest. */
export function numericScale(tokens: Record<string, string>, prefix: string): TokenEntry[] {
  return tokensByPrefix(tokens, [prefix])
    .filter(({ id }) => /^\d+$/.test(id.slice(prefix.length + 1)))
    .sort((a, b) => Number(a.id.slice(prefix.length + 1)) - Number(b.id.slice(prefix.length + 1)));
}
