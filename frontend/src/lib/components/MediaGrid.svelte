<script lang="ts">
    import { Plus, Image as ImageIcon } from 'lucide-svelte';
    import MediaCard from './MediaCard.svelte';

    export let items: Array<{
        id: number;
        title?: string;
        source_url?: string;
        cover_url?: string;
        rating?: number;
        comment?: string;
    }>;
    export let deleteConfirmId: number | null = null;

    import { createEventDispatcher } from 'svelte';
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

{#if items.length > 0}
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
    <div class="flex flex-col items-center justify-center py-24 animate-fade-in">
        <div class="w-20 h-20 rounded-2xl bg-surface border border-border-subtle flex items-center justify-center mb-4">
            <ImageIcon size={32} class="text-text-muted/30" />
        </div>
        <h3 class="text-lg font-semibold text-text-primary mb-1">Пустая коллекция</h3>
        <p class="text-text-secondary text-sm mb-6 text-center max-w-sm">Добавьте первый элемент, чтобы начать отслеживать свои медиа</p>
        <button 
            on:click={handleAdd}
            class="flex items-center gap-2 px-5 py-2.5 bg-accent text-white rounded-xl hover:bg-accent-hover transition-all shadow-lg shadow-accent-glow"
        >
            <Plus size={18} />
            <span class="font-medium">Добавить первый элемент</span>
        </button>
    </div>
{/if}
