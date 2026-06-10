<script lang="ts">
    import { Plus, Image as ImageIcon, Trash2, X } from 'lucide-svelte';
    import { invalidate } from '$app/navigation';
    import type { Importer } from '$lib/importers';
    import { findImporter } from '$lib/importers';

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
    let isImport = false;
    let importError = '';
    let importState: 'idle' | 'loading' = 'idle';

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

    // Keep formData.source_url in sync with input-bound sourceUrl
    $: formData = { ...formData, source_url: sourceUrl };

    // Reactive: detect importer for the provided source URL
    $: importer = findImporter(sourceUrl);

    async function fetchItems() {
        await invalidate(() => true);
    }

    async function submitItem() {
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
                formData = { title: '', source_url: '', cover_url: '', description: '', rating: 0, comment: '' };
                sourceUrl = '';
                importError = '';
                importState = 'idle';
                isImport = false;
                fetchItems();
            } else {
                const err = await res.json();
                alert(err.detail || JSON.stringify(err));
            }
        } catch (e) {
            console.error(e);
        }
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
            // keep input field in sync
            sourceUrl = formData.source_url;
            isImport = true;
        } catch (err) {
            importError = err instanceof Error ? err.message : String(err);
            console.error(err);
        } finally {
            importState = 'idle';
        }
    }

    async function deleteItem(id: number) {
        if (!confirm('Вы уверены, что хотите удалить этот элемент?')) return;
        try {
            const res = await fetch(`http://localhost:8000/api/items/${id}`, { method: 'DELETE' });
            if (res.ok) {
                selectedItem = null; // Закрываем окно просмотра, если оно открыто
                await fetchItems(); // Обновляем список
            }
        } catch (e) {
            console.error("Ошибка при удалении", e);
        }
    }

    function openAddModal() {
        editingId = null;
        formData = { title: '', source_url: '', cover_url: '', description: '', rating: 0, comment: '' };
        sourceUrl = '';
        isImport = false;
        importError = '';
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
        isImport = !!item.source_url;
        importError = '';
        showAddModal = true;
        selectedItem = null;
    }
</script>

<div class="flex justify-between items-center mb-6">
    <h1 class="text-3xl font-bold capitalize text-white">{category.replace('-', ' ')}</h1>
    <button on:click={openAddModal} class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-500 flex items-center gap-2 transition">
        <Plus size={20} /> Добавить
    </button>
</div>

<div class="flex flex-col gap-4">
    {#each items as item}
        <div
            on:click={() => (selectedItem = item)}
            class="flex items-stretch bg-gray-800 rounded-lg shadow border border-gray-700 hover:border-blue-500 hover:bg-gray-750 transition-all text-left overflow-hidden group cursor-pointer"
        >
            <div class="w-24 h-36 shrink-0 bg-gray-700 flex items-center justify-center border-r border-gray-700">
                {#if item.cover_url}
                    <img src={normalizeUrl(item.cover_url)} alt="Обложка" class="w-full h-full object-cover" />
                {:else}
                    <ImageIcon size={32} class="text-gray-500" />
                {/if}
            </div>

            <div class="flex-1 grid grid-cols-4 gap-4 p-4 items-center">
                <div>
                    <h3 class="font-bold text-lg text-white line-clamp-2">
                        <button type="button" on:click|stopPropagation={() => (selectedItem = item)} class="text-left w-full hover:underline">
                            {item.title || 'Без названия'}
                        </button>
                    </h3>
                    {#if item.source_url}
                        <span class="text-xs text-blue-400 mt-1 inline-block">🔗 Импортировано</span>
                    {/if}
                </div>

                <div class="text-sm text-gray-400 line-clamp-3">
                    {item.description || 'Нет описания'}
                </div>

                <div class="flex justify-center">
                    {#if (item.rating ?? 0) > 0}
                        <span class="bg-yellow-900/50 border border-yellow-700 text-yellow-400 font-bold px-3 py-1 rounded-full">
                            ★ {item.rating ?? 0}/10
                        </span>
                    {:else}
                        <span class="text-gray-500 text-sm">Без оценки</span>
                    {/if}
                </div>

                <div class="text-sm text-gray-400 italic line-clamp-3 relative pr-8">
                    {item.comment || 'Нет комментария'}
                    <button
                        on:click|stopPropagation={() => deleteItem(item.id)}
                        class="absolute right-0 top-1/2 -translate-y-1/2 text-gray-500 hover:text-red-500 opacity-0 group-hover:opacity-100 transition cursor-pointer"
                        title="Удалить"
                    >
                        <Trash2 size={20} />
                    </button>
                </div>
            </div>
        </div>
    {:else}
        <div class="text-center text-gray-500 py-10 bg-gray-800 rounded-lg border border-gray-700 border-dashed">
            В этой категории пока ничего нет.
        </div>
    {/each}
</div>

{#if selectedItem}
    <div class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" role="button" tabindex="0" on:click={() => (selectedItem = null)} on:keydown={(e) => e.key === 'Enter' && (selectedItem = null)}>
        <div class="bg-gray-800 p-6 rounded-lg shadow-xl w-full max-w-2xl border border-gray-700 relative" role="dialog" aria-modal="true" tabindex="-1" on:click|stopPropagation on:keydown={() => {}}>
            <button type="button" on:click={() => (selectedItem = null)} class="absolute top-4 right-4 text-gray-400 hover:text-white">
                <X size={24} />
            </button>

            <div class="flex gap-6">
                {#if selectedItem.cover_url}
                    <img src={normalizeUrl(selectedItem.cover_url)} alt="Обложка" class="w-40 h-60 object-cover rounded-md shadow-md" />
                {/if}
                <div class="flex-1 space-y-4">
                    <h2 class="text-3xl font-bold text-white">{selectedItem.title}</h2>
                    <div class="flex items-center gap-3">
                        <span class="bg-yellow-900/50 border border-yellow-700 text-yellow-400 px-3 py-1 rounded-full">★ {selectedItem.rating}/10</span>
                        {#if selectedItem.source_url}
                            <a href={selectedItem.source_url} target="_blank" class="text-blue-400 hover:underline">Перейти к источнику</a>
                        {/if}
                    </div>
                    <div>
                        <h4 class="text-gray-400 text-sm font-semibold mb-1">Описание:</h4>
                        <p class="text-gray-200">{selectedItem.description || '—'}</p>
                    </div>
                    <div>
                        <h4 class="text-gray-400 text-sm font-semibold mb-1">Мой комментарий:</h4>
                        <p class="text-gray-200 italic">{selectedItem.comment || '—'}</p>
                    </div>
                </div>
            </div>

            <div class="mt-6 pt-4 border-t border-gray-700 flex justify-end gap-3">
                <button type="button" on:click={() => selectedItem && editItem(selectedItem)} class="px-4 py-2 bg-yellow-700 text-white rounded-md hover:bg-yellow-600">Редактировать</button>
                <button type="button" on:click={() => selectedItem && deleteItem(selectedItem.id)} class="flex items-center gap-2 px-4 py-2 bg-red-900/50 text-red-400 hover:bg-red-600 hover:text-white rounded-md transition border border-red-800">
                    <Trash2 size={18} /> Удалить элемент
                </button>
            </div>
        </div>
    </div>
{/if}

{#if showAddModal}
    <div class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
        <div class="bg-gray-800 p-6 rounded-lg shadow-xl w-full max-w-md border border-gray-700 max-h-[90vh] overflow-y-auto">
            <h2 class="text-2xl font-bold mb-4 text-white">Добавить элемент</h2>

            <div class="mb-4 flex items-center gap-2 bg-gray-700 p-3 rounded-md">
                <input type="checkbox" id="isImport" bind:checked={isImport} class="w-4 h-4 accent-blue-500" />
                <label for="isImport" class="text-gray-200 cursor-pointer">Импортировать по ссылке</label>
            </div>

            <form on:submit|preventDefault={submitItem} class="space-y-4">
                <div>
                    <label class="block text-sm font-medium mb-1 text-gray-300" for="url">Ссылка на источник</label>
                    <input id="url" type="url" bind:value={sourceUrl} class="w-full bg-gray-900 border border-gray-600 text-white rounded-md p-2 focus:border-blue-500 outline-none" placeholder="https://..." />
                </div>
                {#if formData.source_url}
                    <div class="flex flex-col gap-2">
                        <button type="button" on:click={importFromSource} class="w-full inline-flex justify-center items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-md hover:bg-emerald-500 transition disabled:opacity-50" disabled={!importer || importState === 'loading'}>
                            {#if importState === 'loading'}Импорт...{:else}Импортировать{/if}
                        </button>
                        {#if importer}
                            <p class="text-xs text-gray-400">Импорт настроен для {importer.name}.</p>
                        {:else}
                            <p class="text-xs text-red-400">Ссылка не поддерживается. Вставьте страницу Shikimori.</p>
                        {/if}
                        {#if importError}
                            <p class="text-sm text-red-300">{importError}</p>
                        {/if}
                    </div>
                {/if}

                <div>
                    <label class="block text-sm font-medium mb-1 text-gray-300" for="title">Название {isImport ? '(можно изменить)' : '*'}</label>
                    <input id="title" type="text" bind:value={formData.title} required={!isImport} class="w-full bg-gray-900 border border-gray-600 text-white rounded-md p-2 focus:border-blue-500 outline-none" placeholder="Введите название..." />
                </div>

                <div>
                    <label class="block text-sm font-medium mb-1 text-gray-300" for="cover">Ссылка на обложку</label>
                    <input id="cover" type="url" bind:value={formData.cover_url} class="w-full bg-gray-900 border border-gray-600 text-white rounded-md p-2 focus:border-blue-500 outline-none" />
                </div>

                <div>
                    <label class="block text-sm font-medium mb-1 text-gray-300" for="desc">Описание</label>
                    <textarea id="desc" bind:value={formData.description} class="w-full bg-gray-900 border border-gray-600 text-white rounded-md p-2 focus:border-blue-500 outline-none" rows="3"></textarea>
                </div>

                <div class="flex gap-4">
                    <div class="w-1/3">
                        <label class="block text-sm font-medium mb-1 text-gray-300" for="rating">Оценка (0-10)</label>
                        <input id="rating" type="number" min="0" max="10" bind:value={formData.rating} class="w-full bg-gray-900 border border-gray-600 text-white rounded-md p-2 focus:border-blue-500 outline-none" />
                    </div>
                </div>

                <div>
                    <label class="block text-sm font-medium mb-1 text-gray-300" for="comment">Личное впечатление</label>
                    <textarea id="comment" bind:value={formData.comment} class="w-full bg-gray-900 border border-gray-600 text-white rounded-md p-2 focus:border-blue-500 outline-none" rows="2"></textarea>
                </div>

                <div class="flex justify-end gap-3 mt-6 pt-4 border-t border-gray-700">
                    <button type="button" on:click={() => (showAddModal = false)} class="px-4 py-2 bg-gray-700 text-gray-200 rounded-md hover:bg-gray-600 transition">Отмена</button>
                    <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-500 transition">Сохранить</button>
                </div>
            </form>
        </div>
    </div>
{/if}