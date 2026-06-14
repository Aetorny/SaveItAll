<script lang="ts">
    import { Plus, Search, Filter, X, Tag } from 'lucide-svelte';
    import { slide } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';

    export type FilterState = {
        query: string;
        minRating: number;
        sortBy: 'relevancy' | 'rating' | 'name';
        sortDesc: boolean;
        selectedTags: string[];
        exactMatch: boolean;
    };

    interface Props {
        itemsCount: number;
        filteredCount: number;
        allTags: string[];
        filters: FilterState;
        onAdd: () => void;
        onCreateTag: (tag: string) => void;
        onDeleteTagClick: (tag: string) => void;
    }

    let { itemsCount, filteredCount, allTags, filters = $bindable(), onAdd, onCreateTag, onDeleteTagClick }: Props = $props();

    let showFilters = $state(false);
    let showTagPicker = $state(false);
    let newTagName = $state('');

    function clearSearch() { filters.query = ''; }
    function clearFilters() { filters.minRating = 0; filters.sortBy = 'relevancy'; showFilters = false; }
    function clearTags() { filters.selectedTags = []; }

    function toggleTag(tag: string) {
        if (filters.selectedTags.includes(tag)) {
            filters.selectedTags = filters.selectedTags.filter(t => t !== tag);
        } else {
            filters.selectedTags = [...filters.selectedTags, tag];
        }
    }

    function handleCreateTag() {
        if (newTagName.trim()) {
            onCreateTag(newTagName);
            newTagName = '';
        }
    }
</script>

<div class="flex flex-col gap-4 mb-8 animate-fade-in-up" style="animation-delay: 0.05s">
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
        <div>
            <p class="text-text-secondary text-sm mb-1 flex items-center gap-2">
                <span class="inline-flex items-center w-6 h-6 rounded-lg bg-surface border border-border-subtle text-xs font-bold text-text-primary justify-center">
                    {itemsCount}
                </span>
                {itemsCount === 1 ? 'элемент' : itemsCount < 5 ? 'элемента' : 'элементов'} в коллекции
                {#if filteredCount !== itemsCount}
                    <span class="text-text-muted">· {filteredCount} показано</span>
                {/if}
            </p>
        </div>
        <div class="flex items-center gap-3">
            <button onclick={() => showTagPicker = !showTagPicker} class="flex items-center gap-2 px-4 py-2.5 bg-surface border border-border-subtle text-text-secondary rounded-xl hover:bg-surface-hover text-sm font-medium relative" class:border-accent={showTagPicker} class:text-accent={showTagPicker}>
                <Tag size={16} /><span>Теги</span>
                {#if filters.selectedTags.length > 0}
                    <span class="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full bg-accent text-white text-[10px] font-bold flex items-center justify-center">{filters.selectedTags.length}</span>
                {/if}
            </button>
            <button onclick={() => showFilters = !showFilters} class="flex items-center gap-2 px-4 py-2.5 bg-surface border border-border-subtle text-text-secondary rounded-xl hover:bg-surface-hover text-sm font-medium" class:border-accent={showFilters} class:text-accent={showFilters}>
                <Filter size={16} /><span>Фильтры</span>
            </button>
            <button onclick={onAdd} class="group flex items-center gap-2 px-5 py-2.5 bg-accent text-white rounded-xl hover:bg-accent-hover shadow-lg shadow-accent-glow">
                <Plus size={18} class="transition-transform duration-150 group-hover:rotate-90" />
                <span class="font-medium">Добавить</span>
            </button>
        </div>
    </div>

    <div class="search-input rounded-xl flex items-center gap-3 px-4 py-3">
        <Search size={18} class="text-text-muted shrink-0" />
        <input type="text" bind:value={filters.query} placeholder="Поиск по коллекции..." class="flex-1 bg-transparent border-none outline-none text-sm text-text-primary placeholder:text-text-muted" />
        {#if filters.query}
            <button onclick={clearSearch} class="w-6 h-6 rounded-full bg-surface-hover flex items-center justify-center text-text-muted hover:text-text-primary"><X size={14} /></button>
        {/if}
    </div>
    <!-- Теги -->
    {#if showTagPicker}
        <div class="glass-panel rounded-xl p-4 space-y-3" transition:slide={{ duration: 150, easing: quintOut }}>
            <div class="flex items-center justify-between">
                <span class="text-xs font-semibold text-text-muted uppercase">Фильтр по тегам</span>
                <label class="flex items-center gap-2 text-xs text-text-secondary cursor-pointer">
                    <input type="checkbox" bind:checked={filters.exactMatch} class="accent-accent rounded" /> Точное совпадение
                </label>
            </div>
            {#if allTags.length > 0}
                <div class="flex flex-wrap gap-2">
                    {#each allTags as tag}
                        <div class="group relative">
                            <button onclick={() => toggleTag(tag)} class="px-3 py-1.5 rounded-lg text-xs font-medium border {filters.selectedTags.includes(tag) ? 'bg-accent text-white border-accent' : 'bg-surface text-text-secondary border-border-subtle hover:bg-surface-hover'}">{tag}</button>
                            <button onclick={() => onDeleteTagClick(tag)} class="absolute -top-1.5 -right-1.5 w-4 h-4 rounded-full bg-danger text-white flex items-center justify-center opacity-0 group-hover:opacity-100 hover:scale-110"><X size={8} strokeWidth={3} /></button>
                        </div>
                    {/each}
                </div>
            {:else}
                <p class="text-xs text-text-muted">Нет доступных тегов</p>
            {/if}
            <div class="flex gap-2 pt-2 border-t border-border-subtle">
                <input type="text" bind:value={newTagName} placeholder="Новый тег..." class="flex-1 bg-surface border border-border-subtle text-text-primary rounded-xl px-3 py-2 text-xs focus:border-accent outline-none" />
                <button onclick={handleCreateTag} class="px-3 py-2 bg-success-soft text-success rounded-xl hover:bg-success hover:text-white text-xs font-medium">Создать</button>
            </div>
            {#if filters.selectedTags.length > 0}
                <button onclick={clearTags} class="text-xs text-text-muted hover:text-text-secondary flex items-center gap-1"><X size={12} /> Сбросить теги</button>
            {/if}
        </div>
    {/if}

    {#if showFilters}
        <div class="glass-panel rounded-xl p-4 space-y-4" transition:slide={{ duration: 150, easing: quintOut }}>
            <div class="flex flex-wrap items-center gap-4">
                <div class="flex items-center gap-2">
                    <span class="text-xs text-text-muted uppercase font-semibold">Мин. оценка:</span>
                    <div class="flex gap-1">
                        {#each [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10] as rating}
                            <button onclick={() => filters.minRating = rating} class="px-3 py-1.5 rounded-lg text-xs font-medium {filters.minRating === rating ? 'bg-accent text-white' : 'bg-surface text-text-secondary hover:bg-surface-hover'}">{rating === 0 ? 'Все' : `${rating}+`}</button>
                        {/each}
                    </div>
                </div>
                <div class="w-px h-6 bg-border-subtle"></div>
                <div class="flex items-center gap-2">
                    <span class="text-xs text-text-muted uppercase font-semibold">Сортировка:</span>
                    <div class="flex gap-1">
                        {#each [['relevancy', 'По релевантности'], ['rating', 'По оценке'], ['name', 'По имени']] as [value, label]}
                            <button onclick={() => filters.sortBy = value as any} class="px-3 py-1.5 rounded-lg text-xs font-medium {filters.sortBy === value ? 'bg-accent text-white' : 'bg-surface text-text-secondary hover:bg-surface-hover'}">{label}</button>
                        {/each}
                        <button onclick={() => filters.sortDesc = !filters.sortDesc} class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-surface text-text-secondary hover:bg-surface-hover hover:text-text-primary">
                            <span>{filters.sortDesc ? 'По убыванию' : 'По возрастанию'}</span>
                            <svg class="w-3.5 h-3.5 transition-transform {filters.sortDesc ? '' : 'rotate-180'}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 14l-7 7m0 0l-7-7m7 7V3" /></svg>
                        </button>
                    </div>
                </div>
                <div class="ml-auto">
                    <button onclick={clearFilters} class="text-xs text-text-muted hover:text-text-secondary flex items-center gap-1"><X size={12} /> Сбросить</button>
                </div>
            </div>
        </div>
    {/if}
</div>