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

export const cardAccents = ['none', 'success', 'warning', 'danger'] as const;
export type CardAccent = (typeof cardAccents)[number];

const cardAccentClasses: Record<CardAccent, string> = {
  none: '',
  success: 'border-t-(length:--ds-border-width-strong) border-t-success-border',
  warning: 'border-t-(length:--ds-border-width-strong) border-t-actor-you-border',
  danger: 'border-t-(length:--ds-border-width-strong) border-t-danger-border',
};

/** design.md cards: no border, card inset padding and card stack spacing (D-008). The accent is a top edge. */
export function cardClasses(accent: CardAccent = 'none'): string {
  return ['bg-surface-default rounded-16 flex flex-col gap-(--ds-space-stack-card) p-(--ds-space-inset-card)', cardAccentClasses[accent]]
    .filter(Boolean)
    .join(' ');
}

export const linkCardClasses =
  'bg-surface-default hover:bg-surface-hovered rounded-16 flex h-full flex-col gap-(--ds-space-stack-card) p-(--ds-space-inset-card)';

export const calloutAppearances = ['note', 'example'] as const;
export type CalloutAppearance = (typeof calloutAppearances)[number];

const calloutAppearanceClasses: Record<CalloutAppearance, string> = {
  note: 'border-(length:--ds-border-width-default) border-dashed border-border-default',
  example: '',
};

export function calloutClasses(appearance: CalloutAppearance = 'note'): string {
  return ['bg-surface-subtle rounded-12 type-text-medium flex items-start gap-(--ds-space-12) p-(--ds-space-12)', calloutAppearanceClasses[appearance]]
    .filter(Boolean)
    .join(' ');
}

export const copyLabels = { idle: 'Copy', copied: 'Copied', failed: 'Copy failed' } as const;
export type CopyLabel = (typeof copyLabels)[keyof typeof copyLabels];

/** Copies text and returns the label the button should show next. */
export async function copyToClipboard(
  clipboard: Pick<Clipboard, 'writeText'> | undefined,
  text: string,
): Promise<CopyLabel> {
  try {
    if (!clipboard) return copyLabels.failed;
    await clipboard.writeText(text);
    return copyLabels.copied;
  } catch {
    return copyLabels.failed;
  }
}

/** Visible labels for the actor badge tones. */
export const badgeLabels: Record<BadgeTone, string> = { skill: 'Skill', you: 'You' };

export const pageHeaderSizes = ['large', 'small'] as const;
export type PageHeaderSize = (typeof pageHeaderSizes)[number];

const pageTitleSizeClasses: Record<PageHeaderSize, string> = {
  large: 'type-display-small sm:type-display-large',
  small: 'type-display-small',
};

/** Large titles drop to display-small below 640px. */
export function pageTitleClasses(size: PageHeaderSize = 'large'): string {
  return `${pageTitleSizeClasses[size]} break-words`;
}

/** The id of a step disclosure, used by links that open it. */
export function disclosureId(prefix: string, number: number): string {
  return `${prefix}-${number}`;
}
