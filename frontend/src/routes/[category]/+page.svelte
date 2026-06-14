<script lang="ts">
    import { AlertTriangle } from 'lucide-svelte';
    import { fade } from 'svelte/transition';
    import { invalidate } from '$app/navigation';
    import { findImporter } from '$lib/index';
    
    import { api } from '$lib/api';
    import { toastStore } from '$lib/states/toasts.svelte';
    import CollectionToolbar, { type FilterState } from '$lib/components/CollectionToolbar.svelte';
    
    import MediaGrid from '$lib/components/MediaGrid.svelte';
    import DetailOverlay from '$lib/components/DetailOverlay.svelte';
    import ItemModal from '$lib/components/ItemModal.svelte';
    import Toast from '$lib/components/Toast.svelte';

    type MediaItem = {
        id: number;
        title?: string;
        source_url?: string;
        cover_url?: string;
        description?: string;
        rating?: number;
        comment?: string;
        created_at?: string;
        tags?: string[];
    };

    let { data } = $props();

    let items = $derived<MediaItem[]>(data.items ?? []);
    let allTags = $derived(data.allTags ?? []);
    let error = $derived(data.error ?? '');

    let selectedItem = $state<any | null>(null);
    let showModal = $state(false);
    let editingId = $state<number | null>(null);
    let deleteConfirmId = $state<number | null>(null);
    let tagToDelete = $state<string | null>(null);

    let formData = $state({ title: '', source_url: '', cover_url: '', description: '', rating: 0, comment: '' });
    let itemTags = $state<string[]>([]);
    let sourceUrl = $state('');
    let importError = $state('');
    let importState = $state<'idle' | 'loading'>('idle');
    let importer = $derived(findImporter(sourceUrl));

    let filters = $state<FilterState>({
        query: '', minRating: 0, sortBy: 'relevancy', sortDesc: true, selectedTags: [], exactMatch: false
    });

    const collator = new Intl.Collator(undefined, { numeric: true, sensitivity: 'base' });

    let filteredItems = $derived.by(() => {
        let result = items;

        if (filters.query.trim()) {
            const q = filters.query.toLowerCase();
            result = result.filter(i =>
             i.title?.toLowerCase().includes(q)
             || i.description?.toLowerCase().includes(q)
             || i.comment?.toLowerCase().includes(q)
        );
        }
        if (filters.minRating > 0) {
            result = result.filter(i => (i.rating ?? 0) >= filters.minRating);
        }
        if (filters.selectedTags.length > 0) {
            result = result.filter(i => {
                const tags = i.tags ?? [];
                return filters.exactMatch 
                    ? filters.selectedTags.every(t => tags.includes(t)) 
                    : filters.selectedTags.some(t => tags.includes(t));
            });
        }

        if (filters.sortBy === 'relevancy' && !filters.sortDesc) {
            return result;
        }

        const sortedResult = [...result];

        if (filters.sortBy === 'rating') {
            sortedResult.sort((a, b) => (b.rating ?? 0) - (a.rating ?? 0));
        } else if (filters.sortBy === 'name') {
            sortedResult.sort((a, b) => collator.compare(a.title ?? '', b.title ?? ''));
        }

        if (filters.sortDesc) {
            sortedResult.reverse();
        }

        return sortedResult;
    });

    async function fetchItems() { await invalidate(() => true); }

    async function createGlobalTag(tag: string) {
        if (!tag.trim()) return;
        try {
            await api.createTag(tag.trim());
            await fetchItems();
            toastStore.add('Тег создан', 'success');
        } catch (e) { toastStore.add('Не удалось создать тег', 'error'); }
    }

    async function deleteGlobalTag(tag: string | null) {
        if (!tag) return;
        try {
            await api.deleteTag(tag);
            filters.selectedTags = filters.selectedTags.filter(t => t !== tag);
            await fetchItems();
            toastStore.add('Тег удалён', 'success');
        } catch (e) { toastStore.add('Не удалось удалить тег', 'error'); }
    }

    async function submitItem() {
        const payload = { ...formData, category: data.category, is_import: !!importer && !!formData.source_url, tags: itemTags };
        try {
            await api.saveItem(payload, editingId);
            closeModal();
            fetchItems();
            toastStore.add(editingId ? 'Элемент обновлён' : 'Элемент добавлен', 'success');
        } catch (e: any) { toastStore.add(e.message, 'error'); }
    }

    async function deleteItem(id: number) {
        if (deleteConfirmId !== id) {
            deleteConfirmId = id;
            setTimeout(() => { if (deleteConfirmId === id) deleteConfirmId = null; }, 3000);
            return;
        }
        try {
            await api.deleteItem(id);
            selectedItem = null; deleteConfirmId = null;
            await fetchItems();
            toastStore.add('Элемент удалён', 'success');
        } catch (e) { toastStore.add('Ошибка при удалении', 'error'); }
    }

    function openAddModal() {
        editingId = null;
        formData = { title: '', source_url: '', cover_url: '', description: '', rating: 0, comment: '' };
        sourceUrl = ''; itemTags = []; importError = ''; showModal = true;
    }

    function openEditModal(item: any) {
        editingId = item.id;
        formData = { ...item };
        sourceUrl = item.source_url || '';
        itemTags = [...(item.tags ?? [])];
        showModal = true; selectedItem = null;
    }

    function closeModal() { showModal = false; editingId = null; }

    function handleKeydown(e: KeyboardEvent) {
        if (e.key === 'Escape') { selectedItem = null; closeModal(); }
    }
</script>

<svelte:window on:keydown={handleKeydown} />

<div class="fixed bottom-6 right-6 z-[100] flex flex-col gap-2 pointer-events-none">
    {#each toastStore.toasts as toast (toast.id)}
        <div class="pointer-events-auto">
            <Toast message={toast.message} type={toast.type} on:close={() => toastStore.remove(toast.id)} />
        </div>
    {/each}
</div>

<CollectionToolbar 
    itemsCount={items.length} 
    filteredCount={filteredItems.length}
    {allTags}
    bind:filters
    onAdd={openAddModal}
    onCreateTag={createGlobalTag}
    onDeleteTagClick={(tag) => tagToDelete = tag}
/>

{#if error}
    <div class="mb-6 p-4 rounded-xl bg-danger-soft border border-danger/20 text-danger animate-fade-in flex items-center gap-3" transition:fade>
        <AlertTriangle size={18} /> <p class="text-sm">{error}</p>
    </div>
{/if}

<MediaGrid 
    items={filteredItems} {filters} {deleteConfirmId}
    on:add={openAddModal} on:select={(e) => selectedItem = e.detail}
    on:edit={(e) => openEditModal(e.detail)} on:delete={(e) => deleteItem(e.detail)}
/>

{#if selectedItem}
    <DetailOverlay
        item={selectedItem} {deleteConfirmId} {allTags}
        on:close={() => selectedItem = null} on:edit={(e) => openEditModal(e.detail)}
        on:delete={(e) => deleteItem(e.detail)}
        on:addTag={async (e) => { await api.addTagToItem(e.detail.itemId, e.detail.tag); fetchItems(); }}
        on:removeTag={async (e) => { await api.removeTagFromItem(e.detail.itemId, e.detail.tag); fetchItems(); }}
        on:createTagAndAdd={async (e) => { await createGlobalTag(e.detail.tag); await api.addTagToItem(e.detail.itemId, e.detail.tag); fetchItems(); }}
    />
{/if}

<ItemModal
    show={showModal} {editingId} {formData} {itemTags} {allTags} {sourceUrl} {importer} {importError} {importState}
    on:close={closeModal} on:submit={submitItem} on:createTag={(e) => createGlobalTag(e.detail)}
    on:sourceUrlChange={(e) => sourceUrl = e.detail}
    on:toggleTag={(e) => {
        itemTags = itemTags.includes(e.detail) ? itemTags.filter(t => t !== e.detail) : [...itemTags, e.detail];
    }}
/>

{#if tagToDelete}
    <div class="fixed inset-0 z-[60] flex items-center justify-center p-4">
         <div class="absolute inset-0 modal-overlay" onclick={() => tagToDelete = null}></div>
         <div class="relative w-full max-w-sm glass-panel-strong rounded-2xl p-6 shadow-2xl">
             <h3 class="text-lg font-bold text-text-primary mb-2">Удалить тег?</h3>
             <button onclick={() => { deleteGlobalTag(tagToDelete); tagToDelete = null; }}>Удалить</button>
         </div>
    </div>
{/if}