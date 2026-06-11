<script lang="ts">
    import { Plus, Search, Filter, X, AlertTriangle } from 'lucide-svelte';
    import { invalidate } from '$app/navigation';
    import { findImporter, type ImportedMediaData } from '$lib/index';
    import MediaGrid from '$lib/components/MediaGrid.svelte';
    import DetailOverlay from '$lib/components/DetailOverlay.svelte';
    import ItemModal from '$lib/components/ItemModal.svelte';
    import Toast from '$lib/components/Toast.svelte';
    import { fade, slide } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';

    type MediaItem = {
        id: number;
        title?: string;
        source_url?: string;
        cover_url?: string;
        description?: string;
        rating?: number;
        comment?: string;
        created_at?: string;
    };

    interface Props {
        data: {
            category: string;
            items: MediaItem[];
            error?: string;
        };
    }

    let { data }: Props = $props();

    let selectedItem = $state<MediaItem | null>(null);
    let showModal = $state(false);
    let editingId = $state<number | null>(null);
    let deleteConfirmId = $state<number | null>(null);

    let searchQuery = $state('');
    let showFilters = $state(false);
    let minRating = $state(0);
    let sortBy = $state<'relevancy' | 'rating' | 'name'>('relevancy');

    let toasts = $state<
        Array<{
            id: number;
            message: string;
            type: 'success' | 'error' | 'info';
            duration?: number;
        }>
    >([]);

    let toastId = 0;

    let formData = $state({
        title: '',
        source_url: '',
        cover_url: '',
        description: '',
        rating: 0,
        comment: ''
    });

    let sourceUrl = $state('');
    let importError = $state('');
    let importState = $state<'idle' | 'loading'>('idle');

    let category = $derived(data.category);
    let items = $derived(data.items ?? []);
    let error = $derived(data.error ?? '');

    let importer = $derived(findImporter(sourceUrl));
    let filteredItems = $derived.by(() => {
        let result = items;

        if (searchQuery.trim()) {
            const q = searchQuery.toLowerCase();
            result = result.filter(item =>
                item.title?.toLowerCase().includes(q) ||
                item.description?.toLowerCase().includes(q) ||
                item.comment?.toLowerCase().includes(q)
            );
        }

        if (minRating > 0) {
            result = result.filter(item => (item.rating ?? 0) >= minRating);
        }

        if (sortBy === 'rating') {
            result = [...result].sort((a, b) => (b.rating ?? 0) - (a.rating ?? 0));
        } else if (sortBy === 'name') {
            result = [...result].sort((a, b) =>
                (a.title ?? '').localeCompare(b.title ?? '')
            );
        }

        return result;
    });

    function addToast(message: string, type: 'success' | 'error' | 'info' = 'info', duration = 3000) {
        const id = ++toastId;
        toasts = [...toasts, { id, message, type, duration }];
        setTimeout(() => {
            toasts = toasts.filter(t => t.id !== id);
        }, duration);
    }

    function removeToast(id: number) {
        toasts = toasts.filter(t => t.id !== id);
    }

    $effect(() => {
        items = data?.items ?? [];
    });

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
                addToast(editingId ? 'Элемент обновлён' : 'Элемент добавлен', 'success');
            } else {
                const err = await res.json();
                addToast(err.detail || 'Произошла ошибка', 'error');
            }
        } catch (e) {
            console.error(e);
            addToast('Ошибка сети', 'error');
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
                addToast('Элемент удалён', 'success');
            } else {
                addToast('Не удалось удалить элемент', 'error');
            }
        } catch (e) {
            console.error('Ошибка при удалении', e);
            addToast('Ошибка сети при удалении', 'error');
        }
    }

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
        return u;
    }

    async function importFromSource() {
        formData.source_url = sourceUrl.trim();
        if (!importer || !formData.source_url) {
            importError = 'Ссылка не поддерживается для импорта.';
            return;
        }
        importError = '';
        importState = 'loading';
        try {
            let importedData: ImportedMediaData;

            if (importer.fetchAndParse) {
                importedData = await importer.fetchAndParse(formData.source_url);
            } else if (importer.parseHtml) {
                const html = await fetchHtmlFromUrl(formData.source_url);
                importedData = importer.parseHtml(html, formData.source_url);
            } else {
                throw new Error("У импортера нет метода обработки данных.");
            }

            formData = {
                ...formData,
                title: importedData.title ?? formData.title,
                description: importedData.description ? stripHtml(importedData.description) : formData.description,
                cover_url: importedData.cover_url ? normalizeUrl(importedData.cover_url) ?? formData.cover_url : formData.cover_url,
                source_url: importedData.source_url,
            };
            sourceUrl = formData.source_url;
            addToast(`Импортировано из ${importer.name}`, 'success');
        } catch (err) {
            importError = err instanceof Error ? err.message : String(err);
            addToast('Ошибка импорта', 'error');
            console.error(err);
        } finally {
            importState = 'idle';
        }
    }

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

    function clearSearch() {
        searchQuery = '';
    }

    function clearFilters() {
        minRating = 0;
        sortBy = 'relevancy';
        showFilters = false;
    }

    function handleKeydown(e: KeyboardEvent) {
        if (e.key === 'Escape') {
            if (selectedItem) selectedItem = null;
            if (showModal) closeModal();
        }
    }
</script>

<svelte:window on:keydown={handleKeydown} />

<div class="fixed bottom-6 right-6 z-[100] flex flex-col gap-2 pointer-events-none">
    {#each toasts as toast (toast.id)}
        <div class="pointer-events-auto">
            <Toast 
                message={toast.message} 
                type={toast.type} 
                on:close={() => removeToast(toast.id)}
            />
        </div>
    {/each}
</div>

<div class="flex flex-col gap-4 mb-8 animate-fade-in-up" style="animation-delay: 0.05s">
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
        <div>
            <p class="text-text-secondary text-sm mb-1 flex items-center gap-2">
                <span class="inline-flex items-center justify-center w-6 h-6 rounded-lg bg-surface border border-border-subtle text-xs font-bold text-text-primary">
                    {items.length}
                </span>
                {items.length === 1 ? 'элемент' : items.length < 5 ? 'элемента' : 'элементов'} в коллекции
                {#if filteredItems.length !== items.length}
                    <span class="text-text-muted">· {filteredItems.length} показано</span>
                {/if}
            </p>
        </div>
        <div class="flex items-center gap-3">
            <button 
                onclick={() => showFilters = !showFilters}
                class="flex items-center gap-2 px-4 py-2.5 bg-surface border border-border-subtle text-text-secondary rounded-xl hover:bg-surface-hover hover:border-border-hover transition-all duration-100 text-sm font-medium"
                class:border-accent={showFilters}
                class:text-accent={showFilters}
            >
                <Filter size={16} />
                <span>Фильтры</span>
            </button>
            <button 
                onclick={openAddModal} 
                class="group flex items-center gap-2 px-5 py-2.5 bg-accent text-white rounded-xl hover:bg-accent-hover transition-all duration-100 shadow-lg shadow-accent-glow hover:shadow-xl hover:shadow-accent-glow active:scale-95"
            >
                <Plus size={18} class="transition-transform duration-150 group-hover:rotate-90" />
                <span class="font-medium">Добавить</span>
            </button>
        </div>
    </div>

    <div class="search-input rounded-xl flex items-center gap-3 px-4 py-3">
        <Search size={18} class="text-text-muted shrink-0" />
        <input 
            id="search-input"
            type="text" 
            bind:value={searchQuery}
            placeholder="Поиск по коллекции..."
            class="flex-1 bg-transparent border-none outline-none text-sm text-text-primary placeholder:text-text-muted"
        />
        {#if searchQuery}
            <button 
                onclick={clearSearch}
                class="w-6 h-6 rounded-full bg-surface-hover flex items-center justify-center text-text-muted hover:text-text-primary transition-colors shrink-0"
            >
                <X size={14} />
            </button>
        {/if}
    </div>

    {#if showFilters}
        <div 
            class="glass-panel rounded-xl p-4 space-y-4"
            transition:slide={{ duration: 150, easing: quintOut }}
        >
            <div class="flex flex-wrap items-center gap-4">
                <div class="flex items-center gap-2">
                    <span class="text-xs text-text-muted uppercase tracking-wider font-semibold">Мин. оценка:</span>
                    <div class="flex gap-1">
                        {#each [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10] as rating}
                            <button
                                onclick={() => minRating = rating}
                                class="px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-100 {minRating === rating ? 'bg-accent text-white shadow-lg shadow-accent-glow' : 'bg-surface text-text-secondary hover:bg-surface-hover'}"
                            >
                                {rating === 0 ? 'Все' : `${rating}+`}
                            </button>
                        {/each}
                    </div>
                </div>

                <div class="w-px h-6 bg-border-subtle"></div>

                <div class="flex items-center gap-2">
                    <span class="text-xs text-text-muted uppercase tracking-wider font-semibold">Сортировка:</span>
                    <div class="flex gap-1">
                        {#each [['relevancy', 'По релевантности'], ['rating', 'По оценке'], ['name', 'По имени']] as [value, label]}
                            <button
                                onclick={() => sortBy = value as typeof sortBy}
                                class="px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-100 {sortBy === value ? 'bg-accent text-white shadow-lg shadow-accent-glow' : 'bg-surface text-text-secondary hover:bg-surface-hover'}"
                            >
                                {label}
                            </button>
                        {/each}
                    </div>
                </div>

                <div class="ml-auto">
                    <button
                        onclick={clearFilters}
                        class="text-xs text-text-muted hover:text-text-secondary transition-colors flex items-center gap-1"
                    >
                        <X size={12} />
                        Сбросить
                    </button>
                </div>
            </div>
        </div>
    {/if}
</div>

{#if error}
    <div 
        class="mb-6 p-4 rounded-xl bg-danger-soft border border-danger/20 text-danger animate-fade-in flex items-center gap-3"
        transition:fade
    >
        <AlertTriangle size={18} />
        <p class="text-sm">{error}</p>
    </div>
{/if}

<MediaGrid 
    items={filteredItems} 
    {deleteConfirmId}
    on:add={openAddModal}
    on:select={(e) => selectedItem = e.detail}
    on:edit={(e) => openEditModal(e.detail)}
    on:delete={(e) => deleteItem(e.detail)}
/>

{#if selectedItem}
    <DetailOverlay
        item={selectedItem}
        {deleteConfirmId}
        on:close={() => selectedItem = null}
        on:edit={(e) => openEditModal(e.detail)}
        on:delete={(e) => deleteItem(e.detail)}
    />
{/if}

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
    on:sourceUrlChange={(e) => sourceUrl = e.detail}
/>
