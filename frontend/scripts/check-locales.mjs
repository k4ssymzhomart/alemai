#!/usr/bin/env node
/**
 * Locale consistency gate (docs/04 §5).
 * Asserts that locales/{kk,ru,en}.json have identical (deep) key sets and
 * that no value is an empty string. Exits 1 with a per-file report otherwise.
 */
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

const LOCALES = ['kk', 'ru', 'en'];

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const localesDir = path.join(scriptDir, '..', 'locales');

/** Flatten a nested object into dot-separated leaf keys. */
function flatten(obj, prefix = '', out = new Map()) {
  for (const [key, value] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key;
    if (value !== null && typeof value === 'object' && !Array.isArray(value)) {
      flatten(value, fullKey, out);
    } else {
      out.set(fullKey, value);
    }
  }
  return out;
}

let failed = false;
const flatByLocale = new Map();

for (const locale of LOCALES) {
  const filePath = path.join(localesDir, `${locale}.json`);
  let raw;
  try {
    raw = await readFile(filePath, 'utf8');
  } catch (error) {
    console.error(`ERROR: cannot read ${filePath}: ${error.message}`);
    process.exit(1);
  }
  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch (error) {
    console.error(`ERROR: invalid JSON in ${locale}.json: ${error.message}`);
    process.exit(1);
  }
  flatByLocale.set(locale, flatten(parsed));
}

const allKeys = new Set();
for (const flat of flatByLocale.values()) {
  for (const key of flat.keys()) {
    allKeys.add(key);
  }
}

for (const locale of LOCALES) {
  const flat = flatByLocale.get(locale);

  const missing = [...allKeys].filter((key) => !flat.has(key)).sort();
  if (missing.length > 0) {
    failed = true;
    console.error(`${locale}.json is missing ${missing.length} key(s):`);
    for (const key of missing) {
      console.error(`  - ${key}`);
    }
  }

  const invalid = [...flat.entries()]
    .filter(([, value]) => typeof value !== 'string' || value.trim() === '')
    .map(([key]) => key)
    .sort();
  if (invalid.length > 0) {
    failed = true;
    console.error(
      `${locale}.json has ${invalid.length} empty or non-string value(s):`,
    );
    for (const key of invalid) {
      console.error(`  - ${key}`);
    }
  }
}

if (failed) {
  process.exit(1);
}

console.log(`OK: ${allKeys.size} keys x ${LOCALES.length} locales`);
