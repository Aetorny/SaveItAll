<script lang="ts">
    import { Plus, Image as ImageIcon, SearchX, Sparkles } from 'lucide-svelte';
    import MediaCard from './MediaCard.svelte';
    import { createEventDispatcher } from 'svelte';
    import { fade } from 'svelte/transition';

    interface Props {
        items: Array<{
            id: number;
            title?: string;
            source_url?: string;
            cover_url?: string;
            rating?: number;
            comment?: string;
        }>;
        deleteConfirmId?: number | null;
        loading?: boolean;
    }

    let { items, deleteConfirmId = null, loading = false }: Props = $props();

    const dispatch = createEventDispatcher<{
        add: void;
        select: typeof items[0];
        edit: typeof items[0];
        delete: number;
    }>();

    function handleAdd() {
        dispatch('add');
    }

    function handleSelect(e: CustomEvent) {
        dispatch('select', e.detail);
    }

    function handleEdit(e: CustomEvent) {
        dispatch('edit', e.detail);
    }

    function handleDelete(e: CustomEvent) {
        dispatch('delete', e.detail);
    }
</script>

{#if loading}
    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-5">
        {#each Array(12) as _, index}
            <div class="animate-fade-in-up" style="animation-delay: {index * 0.02}s">
                <div class="poster-aspect rounded-xl skeleton"></div>
                <div class="mt-3 h-4 w-3/4 rounded skeleton"></div>
                <div class="mt-2 h-3 w-1/2 rounded skeleton"></div>
            </div>
        {/each}
    </div>
{:else if items.length > 0}
    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-5">
        {#each items as item, index (item.id)}
            <MediaCard 
                {item} 
                {index} 
                {deleteConfirmId}
                on:click={handleSelect}
                on:edit={handleEdit}
                on:delete={handleDelete}
            />
        {/each}
    </div>
{:else}
    <div class="flex flex-col items-center justify-center py-24 animate-fade-in" in:fade={{ duration: 200 }}>
        <div class="relative mb-6">
            <div class="absolute inset-0 bg-accent/10 blur-2xl rounded-full scale-150"></div>
            <div class="relative w-24 h-24 rounded-2xl bg-surface border border-border-subtle flex items-center justify-center empty-state-icon">
                <SearchX size={40} class="text-text-muted/30" />
            </div>
        </div>
        <h3 class="text-xl font-bold text-text-primary mb-2">Ничего не найдено</h3>
        <p class="text-text-secondary text-sm mb-8 text-center max-w-sm leading-relaxed">
            Попробуйте изменить параметры поиска или добавьте новый элемент в коллекцию
        </p>
        <button 
            onclick={handleAdd}
            class="group flex items-center gap-2 px-6 py-3 bg-accent text-white rounded-xl hover:bg-accent-hover transition-all duration-300 shadow-lg shadow-accent-glow hover:shadow-xl active:scale-95"
        >
            <Plus size={18} class="transition-transform duration-150 group-hover:rotate-90" />
            <span class="font-medium">Добавить элемент</span>
            <Sparkles size={14} class="text-white/60 group-hover:text-white transition-colors" />
        </button>
    </div>
{/if}
