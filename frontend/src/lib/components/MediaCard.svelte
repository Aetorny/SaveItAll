<script lang="ts">
    import { Image as ImageIcon, Star, Sparkles } from 'lucide-svelte';
    import { fly } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';

    export let item: {
        id: number;
        title?: string;
        source_url?: string;
        cover_url?: string;
        rating?: number;
        comment?: string;
    };
    export let index: number = 0;
    export let deleteConfirmId: number | null = null;

    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher<{
        click: typeof item;
        edit: typeof item;
        delete: number;
    }>();

    function normalizeUrl(u: string | null | undefined) {
        if (!u) return u;
        if (u.startsWith('//')) return 'https:' + u;
        if (u.startsWith('/')) return 'https://shikimori.io' + u;
        return u;
    }

    function handleCardClick() {
        dispatch('click', item);
    }

    function handleEditClick(e: Event) {
        e.stopPropagation();
        dispatch('edit', item);
    }

    function handleDeleteClick(e: Event) {
        e.stopPropagation();
        dispatch('delete', item.id);
    }

    function handleKeydown(e: KeyboardEvent) {
        if (e.key === 'Enter') handleCardClick();
    }
</script>

<div 
    class="group relative animate-fade-in-up"
    style="animation-delay: {Math.min(index * 0.05, 0.3)}s"
    in:fly={{ y: 20, duration: 400, delay: index * 50, easing: quintOut }}
>
    <div
        on:click={handleCardClick}
        on:keydown={handleKeydown}
        role="button"
        tabindex="0"
        class="w-full text-left card-hover cursor-pointer"
    >
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

            {#if (item.rating ?? 0) > 0}
                <div class="absolute top-2 right-2 flex items-center gap-0.5 bg-void/80 backdrop-blur-sm px-2 py-1 rounded-lg border border-border-subtle">
                    <Star size={12} class="text-warning fill-warning" />
                    <span class="text-xs font-bold text-white">{item.rating}</span>
                </div>
            {/if}

            {#if item.source_url}
                <div class="absolute top-2 left-2">
                    <div class="bg-accent/80 backdrop-blur-sm p-1.5 rounded-lg" title="Импортировано">
                        <Sparkles size={12} class="text-white" />
                    </div>
                </div>
            {/if}

            <div class="absolute bottom-0 left-0 right-0 p-3 translate-y-2 opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-300">
                <div class="flex gap-2">
                    <button
                        on:click={handleEditClick}
                        class="flex-1 py-1.5 text-xs font-medium bg-white/10 backdrop-blur-md hover:bg-white/20 text-white rounded-lg transition-colors border border-white/10"
                    >
                        Редактировать
                    </button>
                </div>
            </div>
        </div>

        <div class="mt-2.5 px-0.5">
            <h3 class="font-semibold text-sm text-text-primary line-clamp-2 leading-snug group-hover:text-accent transition-colors">
                {item.title || 'Без названия'}
            </h3>
            {#if item.comment}
                <p class="text-xs text-text-muted mt-0.5 line-clamp-1">{item.comment}</p>
            {/if}
        </div>
    </div>

    <button
        on:click={handleDeleteClick}
        class="absolute -top-2 -right-2 w-7 h-7 rounded-full bg-surface-raised border border-border-subtle flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-200 hover:bg-danger-soft hover:border-danger/30 hover:text-danger z-10"
        title="Удалить"
    >
        {#if deleteConfirmId === item.id}
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-danger"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
        {:else}
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-muted"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
        {/if}
    </button>
</div>
