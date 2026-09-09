import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

const rootDir = join(import.meta.dirname, '..');
const pkg = JSON.parse(readFileSync(join(rootDir, 'package.json'), 'utf-8')) as {
  version: string;
  upstream: string;
};

// The version number does not encode the upstream base (major.minor is
// upstream's, patch is the fork's counter), so package.json `upstream` and the
// README table are the only record of provenance. Keep them in step.
describe('fork versioning', () => {
  it('records the upstream base as <owner>/<repo>@<version>', () => {
    expect(pkg.upstream).toMatch(/^vercel-labs\/skills@\d+\.\d+\.\d+$/);
  });

  it('shares major.minor with the upstream base', () => {
    const upstreamVersion = pkg.upstream.split('@')[1]!;
    const [major, minor] = pkg.version.split('.');
    const [upMajor, upMinor] = upstreamVersion.split('.');
    expect(`${major}.${minor}`).toBe(`${upMajor}.${upMinor}`);
  });

  it('README version table has the row for this version', () => {
    const readme = readFileSync(join(rootDir, 'README.md'), 'utf-8');
    const upstreamVersion = pkg.upstream.split('@')[1]!;
    const row = new RegExp(
      `^\\|\\s*${pkg.version.replace(/\./g, '\\.')}\\s*\\|\\s*${upstreamVersion.replace(/\./g, '\\.')}\\s*\\|`,
      'm'
    );
    expect(readme).toMatch(row);
  });
});
