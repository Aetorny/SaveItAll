<script lang="ts">
    import { X, Star, ExternalLink, Trash2 } from 'lucide-svelte';
    import { fade, scale } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';

    export let item: {
        id: number;
        title?: string;
        source_url?: string;
        cover_url?: string;
        description?: string;
        rating?: number;
        comment?: string;
    } | null;
    export let deleteConfirmId: number | null = null;

    import { createEventDispatcher } from 'svelte';

    // Define the item type without null for events
    type ItemType = {
        id: number;
        title?: string;
        source_url?: string;
        cover_url?: string;
        description?: string;
        rating?: number;
        comment?: string;
    };

    const dispatch = createEventDispatcher<{
        close: void;
        edit: ItemType;
        delete: number;
    }>();

    function normalizeUrl(u: string | null | undefined) {
        if (!u) return u;
        if (u.startsWith('//')) return 'https:' + u;
        if (u.startsWith('/')) return 'https://shikimori.io' + u;
        return u;
    }

    function handleClose() {
        dispatch('close');
    }

    function handleEdit() {
        if (item) dispatch('edit', item);
    }

    function handleDelete() {
        if (item) dispatch('delete', item.id);
    }

    function handleBackdropKeydown(e: KeyboardEvent) {
        if (e.key === 'Enter') handleClose();
    }
</script>

{#if item}
    <div 
        class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-8"
        transition:fade={{ duration: 200 }}
    >
        <div 
            class="absolute inset-0 bg-void/90 backdrop-blur-xl"
            on:click={handleClose}
            role="button"
            tabindex="0"
            on:keydown={handleBackdropKeydown}
        ></div>

        <div 
            class="relative w-full max-w-4xl glass-panel-strong rounded-2xl overflow-hidden shadow-2xl animate-scale-in"
            transition:scale={{ duration: 300, easing: quintOut, start: 0.95 }}
        >
            <button 
                on:click={handleClose}
                class="absolute top-4 right-4 z-10 w-10 h-10 rounded-full bg-void/50 backdrop-blur-md border border-border-subtle flex items-center justify-center text-text-secondary hover:text-white hover:bg-void/80 transition-all"
            >
                <X size={20} />
            </button>

            <div class="flex flex-col md:flex-row">
                <div class="md:w-72 shrink-0 relative">
                    {#if item.cover_url}
                        <img 
                            src={normalizeUrl(item.cover_url)} 
                            alt={item.title || 'Обложка'}
                            class="w-full h-64 md:h-full object-cover"
                        />
                        <div class="absolute inset-0 bg-gradient-to-t from-void via-transparent to-transparent md:bg-gradient-to-r"></div>
                    {:else}
                        <div class="w-full h-64 md:h-full bg-surface flex items-center justify-center">
                            <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="text-text-muted/20"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></svg>
                        </div>
                    {/if}
                </div>

                <div class="flex-1 p-6 md:p-8 flex flex-col">
                    <div class="flex-1">
                        <h2 class="text-2xl md:text-3xl font-bold text-text-primary mb-3 leading-tight">
                            {item.title || 'Без названия'}
                        </h2>

                        <div class="flex flex-wrap items-center gap-3 mb-6">
                            {#if (item.rating ?? 0) > 0}
                                <div class="flex items-center gap-1.5 bg-warning-soft border border-warning/20 px-3 py-1.5 rounded-lg">
                                    <Star size={14} class="text-warning fill-warning" />
                                    <span class="text-sm font-bold text-warning">{item.rating}/10</span>
                                </div>
                            {/if}
                            {#if item.source_url}
                                <a 
                                    href={item.source_url} 
                                    target="_blank" 
                                    rel="noopener"
                                    class="flex items-center gap-1.5 text-xs text-accent hover:text-accent-hover transition-colors bg-accent-glow px-3 py-1.5 rounded-lg border border-accent/10"
                                >
                                    <ExternalLink size={12} />
                                    Источник
                                </a>
                            {/if}
                        </div>

                        {#if item.description}
                            <div class="mb-6">
                                <h4 class="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">Описание</h4>
                                <p class="text-text-secondary text-sm leading-relaxed">{item.description}</p>
                            </div>
                        {/if}

                        {#if item.comment}
                            <div class="mb-6">
                                <h4 class="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">Мои заметки</h4>
                                <div class="bg-surface/50 border border-border-subtle rounded-xl p-4">
                                    <p class="text-text-primary text-sm italic leading-relaxed">{item.comment}</p>
                                </div>
                            </div>
                        {/if}
                    </div>

                    <div class="flex gap-3 pt-6 border-t border-border-subtle mt-auto">
                        <button 
                            on:click={handleEdit}
                            class="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-surface-raised border border-border-subtle text-text-primary rounded-xl hover:bg-surface-hover hover:border-border-hover transition-all font-medium text-sm"
                        >
                            Редактировать
                        </button>
                        <button 
                            on:click={handleDelete}
                            class="flex items-center justify-center gap-2 px-4 py-2.5 bg-danger-soft border border-danger/20 text-danger rounded-xl hover:bg-danger hover:text-white transition-all font-medium text-sm"
                        >
                            <Trash2 size={16} />
                            {deleteConfirmId === item.id ? 'Подтвердить' : 'Удалить'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
{/if}
