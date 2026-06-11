import type { Importer } from './types';
import { shikimoriImporter } from './parsers/shikimori';
import { steamImporter } from './parsers/steam';
import { kinopoiskImporter } from './parsers/kinopoisk';

export * from './types';

export const importers: Importer[] = [
    shikimoriImporter,
    steamImporter,
    kinopoiskImporter,
];

export function findImporter(url: string | undefined): Importer | null {
    if (!url) return null;
    try {
        const normalizedUrl = url.trim();
        if (!normalizedUrl) return null;
        return importers.find((importer) => importer.urlPattern.test(normalizedUrl)) ?? null;
    } catch {
        return null;
    }
}