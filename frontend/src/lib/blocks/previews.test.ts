import { describe, it, expect } from 'vitest';
import { PV, BlockPreview, BrandCtx } from './index';
import { BLOCK_LIBRARY } from '@/types/lab';

describe('PV — preview render functions', () => {
  it('has exactly 40 entries (one per block code)', () => {
    expect(Object.keys(PV)).toHaveLength(40);
  });

  it('every BLOCK_LIBRARY code has a corresponding PV render function', () => {
    for (const block of BLOCK_LIBRARY) {
      expect(
        PV[block.code],
        `PV missing entry for block code: ${block.code}`
      ).toBeDefined();
      expect(typeof PV[block.code]).toBe('function');
    }
  });
});

describe('BlockPreview component', () => {
  it('is a function (React component)', () => {
    expect(typeof BlockPreview).toBe('function');
  });
});

describe('BrandCtx', () => {
  it('is a React context object with a Provider', () => {
    expect(BrandCtx).toBeDefined();
    expect(BrandCtx.Provider).toBeDefined();
  });
});
