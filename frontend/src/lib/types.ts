export type ImportedMediaData = {
    title?: string;
    description?: string;
    cover_url?: string;
    source_url: string;
    tags?: string[];
};

export type Importer = {
    id: string;
    name: string;
    urlPattern: RegExp;
    parseHtml?: (html: string, url: string) => ImportedMediaData;
    fetchAndParse?: (url: string) => Promise<ImportedMediaData>;
};
