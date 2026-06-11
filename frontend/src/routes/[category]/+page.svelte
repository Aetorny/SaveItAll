<script lang="ts">
    import { Plus } from 'lucide-svelte';
    import { invalidate } from '$app/navigation';
    import { findImporter } from '$lib/importers';
    import MediaGrid from '$lib/components/MediaGrid.svelte';
    import DetailOverlay from '$lib/components/DetailOverlay.svelte';
    import ItemModal from '$lib/components/ItemModal.svelte';
    import { fade } from 'svelte/transition';

    type MediaItem = {
        id: number;
        title?: string;
        source_url?: string;
        cover_url?: string;
        description?: string;
        rating?: number;
        comment?: string;
    };

    export let data: {
        category: string;
        items: MediaItem[];
        error?: string;
    };

    // State
    let category: string = data?.category ?? '';
    let items: MediaItem[] = data?.items ?? [];
    let error: string = data?.error ?? '';
    let selectedItem: MediaItem | null = null;
    let showModal = false;
    let editingId: number | null = null;
    let deleteConfirmId: number | null = null;

    // Form state
    let formData = { title: '', source_url: '', cover_url: '', description: '', rating: 0, comment: '' };
    let sourceUrl = '';
    let importError = '';
    let importState: 'idle' | 'loading' = 'idle';

    $: category = data?.category ?? category;
    $: items = data?.items ?? items;
    $: error = data?.error ?? error;
    $: importer = findImporter(sourceUrl);
    $: formData = { ...formData, source_url: sourceUrl };

    // API calls
    async function fetchItems() {
        await invalidate(() => true);
    }

    async function submitItem() {
        const isImport = !!importer && !!formData.source_url;
        const payload = { ...formData, category, is_import: isImport };
        try {
            const url = editingId 
                ? `http://localhost:8000/api/items/${editingId}`
                : `http://localhost:8000/api/items/`;
            const method = editingId ? 'PUT' : 'POST';

            const res = await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                closeModal();
                fetchItems();
            } else {
                const err = await res.json();
                alert(err.detail || JSON.stringify(err));
            }
        } catch (e) {
            console.error(e);
        }
    }

    async function deleteItem(id: number) {
        if (deleteConfirmId !== id) {
            deleteConfirmId = id;
            setTimeout(() => { if (deleteConfirmId === id) deleteConfirmId = null; }, 3000);
            return;
        }
        try {
            const res = await fetch(`http://localhost:8000/api/items/${id}`, { method: 'DELETE' });
            if (res.ok) {
                selectedItem = null;
                deleteConfirmId = null;
                await fetchItems();
            }
        } catch (e) {
            console.error('Ошибка при удалении', e);
        }
    }

    // Import logic
    async function fetchHtmlFromUrl(url: string) {
        try {
            const res = await fetch(url, { method: 'GET', headers: { 'Accept': 'text/html' } });
            if (res.ok) return await res.text();
        } catch (e) {
            console.warn('Direct HTML fetch failed, fallback to proxy', e);
        }
        const proxyUrl = `http://localhost:8000/api/fetch-url?url=${encodeURIComponent(url)}`;
        const proxyRes = await fetch(proxyUrl);
        if (!proxyRes.ok) {
            throw new Error(`Не удалось загрузить страницу: ${await proxyRes.text()}`);
        }
        return await proxyRes.text();
    }

    function stripHtml(html: string | null | undefined) {
        if (!html) return '';
        const doc = new DOMParser().parseFromString(html, 'text/html');
        return (doc.body.textContent || '').trim();
    }

    function normalizeUrl(u: string | null | undefined) {
        if (!u) return u;
        if (u.startsWith('//')) return 'https:' + u;
        if (u.startsWith('/')) return 'https://shikimori.io' + u;
        return u;
    }

    async function importFromSource() {
        if (!importer || !formData.source_url) {
            importError = 'Ссылка не поддерживается для импорта.';
            return;
        }
        importError = '';
        importState = 'loading';
        try {
            const html = await fetchHtmlFromUrl(formData.source_url);
            const data = importer.parseHtml(html, formData.source_url);
            formData = {
                ...formData,
                title: data.title ?? formData.title,
                description: data.description ? stripHtml(data.description) : formData.description,
                cover_url: data.cover_url ? normalizeUrl(data.cover_url) ?? formData.cover_url : formData.cover_url,
                source_url: data.source_url,
            };
            sourceUrl = formData.source_url;
        } catch (err) {
            importError = err instanceof Error ? err.message : String(err);
            console.error(err);
        } finally {
            importState = 'idle';
        }
    }

    // Modal management
    function resetForm() {
        formData = { title: '', source_url: '', cover_url: '', description: '', rating: 0, comment: '' };
        sourceUrl = '';
        importError = '';
        importState = 'idle';
    }

    function openAddModal() {
        editingId = null;
        resetForm();
        showModal = true;
    }

    function openEditModal(item: MediaItem) {
        editingId = item.id;
        formData = {
            title: item.title || '',
            source_url: item.source_url || '',
            cover_url: item.cover_url || '',
            description: item.description || '',
            rating: item.rating || 0,
            comment: item.comment || ''
        };
        sourceUrl = item.source_url || '';
        importError = '';
        showModal = true;
        selectedItem = null;
    }

    function closeModal() {
        showModal = false;
        editingId = null;
        resetForm();
    }

    // Event handlers from components
    function handleSelectItem(e: CustomEvent<MediaItem>) {
        selectedItem = e.detail;
    }

    function handleEditItem(e: CustomEvent<MediaItem>) {
        openEditModal(e.detail);
    }

    function handleDeleteItem(e: CustomEvent<number>) {
        deleteItem(e.detail);
    }

    function handleModalSourceUrlChange(e: CustomEvent<string>) {
        sourceUrl = e.detail;
    }

    function handleKeydown(e: KeyboardEvent) {
        if (e.key === 'Escape') {
            if (selectedItem) selectedItem = null;
            if (showModal) closeModal();
        }
    }
</script>

<svelte:window on:keydown={handleKeydown} />

<!-- Header -->
<div class="flex justify-between items-end mb-8 animate-fade-in-up" style="animation-delay: 0.05s">
    <div>
        <p class="text-text-secondary text-sm mb-1">
            {items.length} {items.length === 1 ? 'элемент' : items.length < 5 ? 'элемента' : 'элементов'}
        </p>
    </div>
    <button 
        on:click={openAddModal} 
        class="group flex items-center gap-2 px-5 py-2.5 bg-accent text-white rounded-xl hover:bg-accent-hover transition-all duration-200 shadow-lg shadow-accent-glow hover:shadow-xl hover:shadow-accent-glow active:scale-95"
    >
        <Plus size={18} class="transition-transform group-hover:rotate-90" />
        <span class="font-medium">Добавить</span>
    </button>
</div>

{#if error}
    <div class="mb-6 p-4 rounded-xl bg-danger-soft border border-danger/20 text-danger animate-fade-in" transition:fade>
        <p class="text-sm">{error}</p>
    </div>
{/if}

<!-- Grid -->
<MediaGrid 
    {items} 
    {deleteConfirmId}
    on:add={openAddModal}
    on:select={handleSelectItem}
    on:edit={handleEditItem}
    on:delete={handleDeleteItem}
/>

<!-- Detail Overlay -->
<DetailOverlay 
    item={selectedItem} 
    {deleteConfirmId}
    on:close={() => selectedItem = null}
    on:edit={handleEditItem}
    on:delete={handleDeleteItem}
/>

<!-- Add/Edit Modal -->
<ItemModal
    show={showModal}
    {editingId}
    {formData}
    {sourceUrl}
    {importer}
    {importError}
    {importState}
    on:close={closeModal}
    on:submit={submitItem}
    on:import={importFromSource}
    on:sourceUrlChange={handleModalSourceUrlChange}
/>
