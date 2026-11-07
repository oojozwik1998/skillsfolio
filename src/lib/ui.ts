/**
 * Variant logic for the design-system components in src/components/ui.
 * Class names are written out in full so Tailwind can find them.
 */

export const iconNames = ['arrow-right', 'chevron-down', 'loop'] as const;
export type IconName = (typeof iconNames)[number];

/** SVG path data on a 16 × 16 grid, drawn with a 1.5 stroke in currentColor. */
export const iconPaths: Record<IconName, string> = {
  'arrow-right': 'M2 8h12M10 4l4 4-4 4',
  'chevron-down': 'M4 6l4 4 4-4',
  loop: 'M2.5 8a5.5 5.5 0 1 0 1.6-3.9L2.5 5.7M2.5 2.5v3.2h3.2',
};

export const linkTones = ['default', 'subtle'] as const;
export type LinkTone = (typeof linkTones)[number];

const linkToneClasses: Record<LinkTone, string> = {
  default: 'text-text-default',
  subtle: 'text-text-subtle',
};

export function linkClasses(tone: LinkTone = 'default'): string {
  return `type-label underline-offset-2 hover:underline ${linkToneClasses[tone]}`;
}

export const badgeTones = ['skill', 'you'] as const;
export type BadgeTone = (typeof badgeTones)[number];

const badgeToneClasses: Record<BadgeTone, string> = {
  skill: 'bg-actor-skill-background text-actor-skill-text',
  you: 'bg-actor-you-background text-actor-you-text',
};

export function badgeClasses(tone: BadgeTone): string {
  return `type-text-small rounded-6 inline-block shrink-0 px-(--ds-space-8) py-(--ds-space-2) ${badgeToneClasses[tone]}`;
}

export const buttonAppearances = ['secondary'] as const;
export type ButtonAppearance = (typeof buttonAppearances)[number];

const buttonAppearanceClasses: Record<ButtonAppearance, string> = {
  secondary:
    'bg-action-secondary-background border-action-secondary-border text-action-secondary-text enabled:hover:bg-action-secondary-hovered enabled:active:bg-action-secondary-pressed',
};

export function buttonClasses(appearance: ButtonAppearance = 'secondary'): string {
  return [
    'type-label rounded-12 inline-flex h-(--ds-size-control-md) shrink-0 cursor-pointer items-center justify-center border-(length:--ds-border-width-default) px-(--ds-space-20)',
    'disabled:bg-surface-subtle disabled:text-text-subtle disabled:cursor-not-allowed',
    buttonAppearanceClasses[appearance],
  ].join(' ');
}
