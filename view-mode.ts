export const ViewMode = {
  Single: 'single',
  Batch: 'batch'
} as const;

export type ViewModeType = typeof ViewMode[keyof typeof ViewMode];
