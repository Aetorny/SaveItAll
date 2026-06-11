export function getMetaContent(doc: Document, selector: string): string | null {
    const el = doc.querySelector(selector) as HTMLMetaElement | null;
    return el?.content?.trim() || null;
}

export function normalizeText(value: string | null | undefined): string | undefined {
    if (!value) return undefined;
    const text = value.trim();
    return text.length ? text : undefined;
}

export function getDescriptionTextFromNode(node: Element | null): string | undefined {
    if (!node) return undefined;
    const rawText = node.textContent?.trim();
    return normalizeText(rawText);
}

export function getDescriptionHtmlFromNode(node: Element | null): string | undefined {
    if (!node) return undefined;
    const html = node.innerHTML?.trim();
    return normalizeText(html);
}