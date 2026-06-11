<script lang="ts">
    import { Plus, Image as ImageIcon, Trash2, X, ExternalLink, Star, Sparkles, Loader2 } from 'lucide-svelte';
    import { invalidate } from '$app/navigation';
    import type { Importer } from '$lib/importers';
    import { findImporter } from '$lib/importers';
    import { fly, fade, scale } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';

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

    let category: string = data?.category ?? '';
    let items: MediaItem[] = data?.items ?? [];
    let error: string = data?.error ?? '';
    let selectedItem: MediaItem | null = null;
    let showAddModal = false;
    let editingId: number | null = null;
    let importer: Importer | null = null;
    let formData = { title: '', source_url: '', cover_url: '', description: '', rating: 0, comment: '' };
    let sourceUrl = '';
    let importError = '';
    let importState: 'idle' | 'loading' = 'idle';
    let deleteConfirmId: number | null = null;

    function stripHtml(html: string | null | undefined) {
        if (!html) return '';
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        return (doc.body.textContent || '').trim();
    }

    function normalizeUrl(u: string | null | undefined) {
        if (!u) return u;
        if (u.startsWith('//')) return 'https:' + u;
        if (u.startsWith('/')) return 'https://shikimori.io' + u;
        return u;
    }

    $: category = data?.category ?? category;
    $: items = data?.items ?? items;
    $: error = data?.error ?? error;
    $: formData = { ...formData, source_url: sourceUrl };
    $: importer = findImporter(sourceUrl);

    async function fetchItems() {
        await invalidate(() => true);
    }

    async function submitItem() {
        const isImport = !!importer && !!formData.source_url;
        const payload = { ...formData, category, is_import: isImport };
        try {
            let res;
            if (editingId) {
                res = await fetch(`http://localhost:8000/api/items/${editingId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
            } else {
                res = await fetch(`http://localhost:8000/api/items/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
            }

            if (res.ok) {
                showAddModal = false;
                editingId = null;
                resetForm();
                fetchItems();
            } else {
                const err = await res.json();
                alert(err.detail || JSON.stringify(err));
            }
        } catch (e) {
            console.error(e);
        }
    }

    function resetForm() {
        formData = { title: '', source_url: '', cover_url: '', description: '', rating: 0, comment: '' };
        sourceUrl = '';
        importError = '';
        importState = 'idle';
    }

    async function fetchHtmlFromUrl(url: string) {
        try {
            const res = await fetch(url, { method: 'GET', headers: { 'Accept': 'text/html' } });
            if (res.ok) {
                return await res.text();
            }
        } catch (e) {
            console.warn('Direct HTML fetch failed, fallback to proxy', e);
        }
        const proxyUrl = `http://localhost:8000/api/fetch-url?url=${encodeURIComponent(url)}`;
        const proxyRes = await fetch(proxyUrl);
        if (!proxyRes.ok) {
            const proxyDetail = await proxyRes.text();
            throw new Error(`Не удалось загрузить страницу: ${proxyDetail}`);
        }
        return await proxyRes.text();
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
            console.error("Ошибка при удалении", e);
        }
    }

    function openAddModal() {
        editingId = null;
        resetForm();
        showAddModal = true;
    }

    function editItem(item: MediaItem) {
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
        showAddModal = true;
        selectedItem = null;
    }

    function renderStars(rating: number = 0) {
        return Array.from({ length: 10 }, (_, i) => i < rating);
    }

    function closeDetail() {
        selectedItem = null;
    }

    function handleKeydown(e: KeyboardEvent) {
        if (e.key === 'Escape') {
            if (selectedItem) selectedItem = null;
            if (showAddModal) showAddModal = false;
        }
    }

    function handleCardClick(item: MediaItem) {
        selectedItem = item;
    }

    function handleEditClick(e: Event, item: MediaItem) {
        e.stopPropagation();
        editItem(item);
    }

    function handleDeleteClick(e: Event, id: number) {
        e.stopPropagation();
        deleteItem(id);
    }
</script>

<svelte:window on:keydown={handleKeydown} />

<!-- Header with add button -->
<div class="flex justify-between items-end mb-8 animate-fade-in-up" style="animation-delay: 0.05s">
    <div>
        <p class="text-text-secondary text-sm mb-1">{items.length} {items.length === 1 ? 'элемент' : items.length < 5 ? 'элемента' : 'элементов'}</p>
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

<!-- Grid of cards -->
{#if items.length > 0}
    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-5">
        {#each items as item, index (item.id)}
            <div 
                class="group relative animate-fade-in-up"
                style="animation-delay: {Math.min(index * 0.05, 0.3)}s"
                in:fly={{ y: 20, duration: 400, delay: index * 50, easing: quintOut }}
            >
                <!-- Card is now a div, not a button -->
                <div
                    on:click={() => handleCardClick(item)}
                    on:keydown={(e) => e.key === 'Enter' && handleCardClick(item)}
                    role="button"
                    tabindex="0"
                    class="w-full text-left card-hover cursor-pointer"
                >
                    <!-- Poster container -->
                    <div class="relative poster-aspect rounded-xl overflow-hidden bg-surface border border-border-subtle group-hover:border-border-hover transition-all">
                        {#if item.cover_url}
                            <img 
                                src={normalizeUrl(item.cover_url)} 
                                alt={item.title || 'Обложка'} 
                                class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                                loading="lazy"
                            />
                            <div class="absolute inset-0 bg-gradient-to-t from-void via-transparent to-transparent opacity-60"></div>
                        {:else}
                            <div class="w-full h-full flex items-center justify-center bg-surface">
                                <ImageIcon size={40} class="text-text-muted/30" />
                            </div>
                        {/if}

                        <!-- Rating badge -->
                        {#if (item.rating ?? 0) > 0}
                            <div class="absolute top-2 right-2 flex items-center gap-0.5 bg-void/80 backdrop-blur-sm px-2 py-1 rounded-lg border border-border-subtle">
                                <Star size={12} class="text-warning fill-warning" />
                                <span class="text-xs font-bold text-white">{item.rating}</span>
                            </div>
                        {/if}

                        <!-- Imported badge -->
                        {#if item.source_url}
                            <div class="absolute top-2 left-2">
                                <div class="bg-accent/80 backdrop-blur-sm p-1.5 rounded-lg" title="Импортировано">
                                    <Sparkles size={12} class="text-white" />
                                </div>
                            </div>
                        {/if}

                        <!-- Hover actions -->
                        <div class="absolute bottom-0 left-0 right-0 p-3 translate-y-2 opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-300">
                            <div class="flex gap-2">
                                <button
                                    on:click={(e) => handleEditClick(e, item)}
                                    class="flex-1 py-1.5 text-xs font-medium bg-white/10 backdrop-blur-md hover:bg-white/20 text-white rounded-lg transition-colors border border-white/10"
                                >
                                    Редактировать
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Title below poster -->
                    <div class="mt-2.5 px-0.5">
                        <h3 class="font-semibold text-sm text-text-primary line-clamp-2 leading-snug group-hover:text-accent transition-colors">
                            {item.title || 'Без названия'}
                        </h3>
                        {#if item.comment}
                            <p class="text-xs text-text-muted mt-0.5 line-clamp-1">{item.comment}</p>
                        {/if}
                    </div>
                </div>

                <!-- Quick delete button (outside the card div) -->
                <button
                    on:click={(e) => handleDeleteClick(e, item.id)}
                    class="absolute -top-2 -right-2 w-7 h-7 rounded-full bg-surface-raised border border-border-subtle flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-200 hover:bg-danger-soft hover:border-danger/30 hover:text-danger z-10"
                    title="Удалить"
                >
                    {#if deleteConfirmId === item.id}
                        <Trash2 size={14} class="text-danger" />
                    {:else}
                        <X size={14} class="text-text-muted" />
                    {/if}
                </button>
            </div>
        {/each}
    </div>
{:else}
    <div class="flex flex-col items-center justify-center py-24 animate-fade-in">
        <div class="w-20 h-20 rounded-2xl bg-surface border border-border-subtle flex items-center justify-center mb-4">
            <ImageIcon size={32} class="text-text-muted/30" />
        </div>
        <h3 class="text-lg font-semibold text-text-primary mb-1">Пустая коллекция</h3>
        <p class="text-text-secondary text-sm mb-6 text-center max-w-sm">Добавьте первый элемент, чтобы начать отслеживать свои медиа</p>
        <button 
            on:click={openAddModal}
            class="flex items-center gap-2 px-5 py-2.5 bg-accent text-white rounded-xl hover:bg-accent-hover transition-all shadow-lg shadow-accent-glow"
        >
            <Plus size={18} />
            <span class="font-medium">Добавить первый элемент</span>
        </button>
    </div>
{/if}

<!-- Detail Overlay -->
{#if selectedItem}
    <div 
        class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-8"
        transition:fade={{ duration: 200 }}
    >
        <div 
            class="absolute inset-0 bg-void/90 backdrop-blur-xl"
            on:click={closeDetail}
            role="button"
            tabindex="0"
            on:keydown={(e) => e.key === 'Enter' && closeDetail()}
        ></div>

        <div 
            class="relative w-full max-w-4xl glass-panel-strong rounded-2xl overflow-hidden shadow-2xl animate-scale-in"
            transition:scale={{ duration: 300, easing: quintOut, start: 0.95 }}
        >
            <button 
                on:click={closeDetail}
                class="absolute top-4 right-4 z-10 w-10 h-10 rounded-full bg-void/50 backdrop-blur-md border border-border-subtle flex items-center justify-center text-text-secondary hover:text-white hover:bg-void/80 transition-all"
            >
                <X size={20} />
            </button>

            <div class="flex flex-col md:flex-row">
                <div class="md:w-72 shrink-0 relative">
                    {#if selectedItem.cover_url}
                        <img 
                            src={normalizeUrl(selectedItem.cover_url)} 
                            alt={selectedItem.title || 'Обложка'}
                            class="w-full h-64 md:h-full object-cover"
                        />
                        <div class="absolute inset-0 bg-gradient-to-t from-void via-transparent to-transparent md:bg-gradient-to-r"></div>
                    {:else}
                        <div class="w-full h-64 md:h-full bg-surface flex items-center justify-center">
                            <ImageIcon size={64} class="text-text-muted/20" />
                        </div>
                    {/if}
                </div>

                <div class="flex-1 p-6 md:p-8 flex flex-col">
                    <div class="flex-1">
                        <h2 class="text-2xl md:text-3xl font-bold text-text-primary mb-3 leading-tight">
                            {selectedItem.title || 'Без названия'}
                        </h2>

                        <div class="flex flex-wrap items-center gap-3 mb-6">
                            {#if (selectedItem.rating ?? 0) > 0}
                                <div class="flex items-center gap-1.5 bg-warning-soft border border-warning/20 px-3 py-1.5 rounded-lg">
                                    <Star size={14} class="text-warning fill-warning" />
                                    <span class="text-sm font-bold text-warning">{selectedItem.rating}/10</span>
                                </div>
                            {/if}
                            {#if selectedItem.source_url}
                                <a 
                                    href={selectedItem.source_url} 
                                    target="_blank" 
                                    rel="noopener"
                                    class="flex items-center gap-1.5 text-xs text-accent hover:text-accent-hover transition-colors bg-accent-glow px-3 py-1.5 rounded-lg border border-accent/10"
                                >
                                    <ExternalLink size={12} />
                                    Источник
                                </a>
                            {/if}
                        </div>

                        {#if selectedItem.description}
                            <div class="mb-6">
                                <h4 class="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">Описание</h4>
                                <p class="text-text-secondary text-sm leading-relaxed">{selectedItem.description}</p>
                            </div>
                        {/if}

                        {#if selectedItem.comment}
                            <div class="mb-6">
                                <h4 class="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">Мои заметки</h4>
                                <div class="bg-surface/50 border border-border-subtle rounded-xl p-4">
                                    <p class="text-text-primary text-sm italic leading-relaxed">{selectedItem.comment}</p>
                                </div>
                            </div>
                        {/if}
                    </div>

                    <div class="flex gap-3 pt-6 border-t border-border-subtle mt-auto">
                        <button 
                            on:click={() => selectedItem && editItem(selectedItem)}
                            class="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-surface-raised border border-border-subtle text-text-primary rounded-xl hover:bg-surface-hover hover:border-border-hover transition-all font-medium text-sm"
                        >
                            Редактировать
                        </button>
                        <button 
                            on:click={() => selectedItem && deleteItem(selectedItem.id)}
                            class="flex items-center justify-center gap-2 px-4 py-2.5 bg-danger-soft border border-danger/20 text-danger rounded-xl hover:bg-danger hover:text-white transition-all font-medium text-sm"
                        >
                            <Trash2 size={16} />
                            {deleteConfirmId === selectedItem.id ? 'Подтвердить' : 'Удалить'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
{/if}

<!-- Add/Edit Modal -->
{#if showAddModal}
    <div 
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        transition:fade={{ duration: 200 }}
    >
        <div 
            class="absolute inset-0 bg-void/80 backdrop-blur-xl"
            on:click={() => showAddModal = false}
            role="button"
            tabindex="0"
            on:keydown={(e) => e.key === 'Enter' && (showAddModal = false)}
        ></div>

        <div 
            class="relative w-full max-w-lg glass-panel-strong rounded-2xl shadow-2xl max-h-[90vh] overflow-y-auto scrollbar-thin animate-scale-in"
            transition:scale={{ duration: 300, easing: quintOut, start: 0.95 }}
        >
            <div class="p-6 md:p-8">
                <div class="flex items-center justify-between mb-6">
                    <h2 class="text-xl font-bold text-text-primary">
                        {editingId ? 'Редактировать' : 'Добавить элемент'}
                    </h2>
                    <button 
                        on:click={() => showAddModal = false}
                        class="w-8 h-8 rounded-lg hover:bg-surface flex items-center justify-center text-text-muted hover:text-text-primary transition-colors"
                    >
                        <X size={18} />
                    </button>
                </div>

                <form on:submit|preventDefault={submitItem} class="space-y-5">
                    <!-- Source URL with auto-import -->
                    <div class="space-y-3">
                        <label class="block text-xs font-semibold text-text-muted uppercase tracking-wider" for="url">Ссылка на источник</label>
                        <div class="flex gap-2">
                            <input 
                                id="url" 
                                type="url" 
                                bind:value={sourceUrl} 
                                class="flex-1 bg-surface border border-border-subtle text-text-primary rounded-xl px-4 py-2.5 text-sm placeholder:text-text-muted focus:border-accent focus:outline-none"
                                placeholder="https://shikimori.io/animes/..."
                            />
                            <button 
                                type="button" 
                                on:click={importFromSource}
                                disabled={!importer || importState === 'loading'}
                                class="px-4 py-2.5 bg-success-soft border border-success/20 text-success rounded-xl hover:bg-success hover:text-white transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2 text-sm font-medium shrink-0"
                            >
                                {#if importState === 'loading'}
                                    <Loader2 size={16} class="animate-spin" />
                                {:else}
                                    <Sparkles size={16} />
                                {/if}
                                Импорт
                            </button>
                        </div>
                        {#if importer}
                            <p class="text-xs text-success flex items-center gap-1">
                                <Sparkles size={12} />
                                Поддерживается импорт из {importer.name}
                            </p>
                        {:else if sourceUrl}
                            <p class="text-xs text-text-muted">Вставьте ссылку на Shikimori для автоматического импорта</p>
                        {/if}
                        {#if importError}
                            <p class="text-xs text-danger bg-danger-soft px-3 py-2 rounded-lg">{importError}</p>
                        {/if}
                    </div>

                    <div class="space-y-3">
                        <label class="block text-xs font-semibold text-text-muted uppercase tracking-wider" for="title">
                            Название {#if !importer || !sourceUrl}<span class="text-danger">*</span>{/if}
                        </label>
                        <input 
                            id="title" 
                            type="text" 
                            bind:value={formData.title} 
                            required={!importer || !sourceUrl}
                            class="w-full bg-surface border border-border-subtle text-text-primary rounded-xl px-4 py-2.5 text-sm placeholder:text-text-muted focus:border-accent focus:outline-none"
                            placeholder="Название медиа..."
                        />
                    </div>

                    <div class="space-y-3">
                        <label class="block text-xs font-semibold text-text-muted uppercase tracking-wider" for="cover">Ссылка на обложку</label>
                        <input 
                            id="cover" 
                            type="url" 
                            bind:value={formData.cover_url} 
                            class="w-full bg-surface border border-border-subtle text-text-primary rounded-xl px-4 py-2.5 text-sm placeholder:text-text-muted focus:border-accent focus:outline-none"
                            placeholder="https://..."
                        />
                    </div>

                    <div class="space-y-3">
                        <label class="block text-xs font-semibold text-text-muted uppercase tracking-wider" for="desc">Описание</label>
                        <textarea 
                            id="desc" 
                            bind:value={formData.description} 
                            class="w-full bg-surface border border-border-subtle text-text-primary rounded-xl px-4 py-2.5 text-sm placeholder:text-text-muted focus:border-accent focus:outline-none resize-none"
                            rows="3"
                            placeholder="Краткое описание..."
                        ></textarea>
                    </div>

                    <div class="space-y-3">
                        <label class="block text-xs font-semibold text-text-muted uppercase tracking-wider" for="rating">
                            Оценка <span class="text-text-secondary font-normal">{formData.rating}/10</span>
                        </label>
                        <div class="flex items-center gap-4">
                            <input 
                                id="rating" 
                                type="range" 
                                min="0" 
                                max="10" 
                                step="1"
                                bind:value={formData.rating} 
                                class="flex-1"
                            />
                            <div class="flex gap-0.5">
                                {#each renderStars(formData.rating) as filled}
                                    <Star size={16} class={filled ? 'text-warning fill-warning' : 'text-text-muted/30'} />
                                {/each}
                            </div>
                        </div>
                    </div>

                    <div class="space-y-3">
                        <label class="block text-xs font-semibold text-text-muted uppercase tracking-wider" for="comment">Личное впечатление</label>
                        <textarea 
                            id="comment" 
                            bind:value={formData.comment} 
                            class="w-full bg-surface border border-border-subtle text-text-primary rounded-xl px-4 py-2.5 text-sm placeholder:text-text-muted focus:border-accent focus:outline-none resize-none"
                            rows="2"
                            placeholder="Ваши мысли об этом..."
                        ></textarea>
                    </div>

                    <div class="flex gap-3 pt-4 border-t border-border-subtle">
                        <button 
                            type="button" 
                            on:click={() => showAddModal = false}
                            class="flex-1 px-4 py-2.5 bg-surface border border-border-subtle text-text-secondary rounded-xl hover:bg-surface-hover hover:text-text-primary transition-all text-sm font-medium"
                        >
                            Отмена
                        </button>
                        <button 
                            type="submit"
                            class="flex-1 px-4 py-2.5 bg-accent text-white rounded-xl hover:bg-accent-hover transition-all shadow-lg shadow-accent-glow text-sm font-medium active:scale-95"
                        >
                            {editingId ? 'Сохранить изменения' : 'Добавить'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
{/if}
