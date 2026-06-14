<script lang="ts">
    import { Image as ImageIcon, Star, Sparkles } from 'lucide-svelte';
    import { fly } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';
    import { createEventDispatcher } from 'svelte';

    interface Props {
        item: {
            id: number;
            title?: string;
            source_url?: string;
            cover_url?: string;
            rating?: number;
            comment?: string;
            tags?: string[];
        };
        index?: number;
        deleteConfirmId?: number | null;
    }

    let { item, index = 0, deleteConfirmId = null }: Props = $props();

    const dispatch = createEventDispatcher<{
        click: typeof item;
        edit: typeof item;
        delete: number;
    }>();

    let cardRef = $state<HTMLDivElement | null>(null);
    let isHovered = $state(false);
    let tiltX = $state(0);
    let tiltY = $state(0);

    function normalizeUrl(u: string | null | undefined) {
        if (!u) return u;
        if (u.startsWith('//')) return 'https:' + u;
        return u;
    }

    function handleMouseMove(e: MouseEvent) {
        if (!cardRef) return;
        const rect = cardRef.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width - 0.5;
        const y = (e.clientY - rect.top) / rect.height - 0.5;
        tiltX = y * -8;
        tiltY = x * 8;
    }

    function handleMouseLeave() {
        isHovered = false;
        tiltX = 0;
        tiltY = 0;
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
    style="animation-delay: 0.1s"
    in:fly={{ y: 24, duration: 250, delay: index < 60 ? index * 20 : 2, easing: quintOut }}
>
    <div
        bind:this={cardRef}
        onclick={handleCardClick}
        onkeydown={handleKeydown}
        onmouseenter={() => isHovered = true}
        onmousemove={handleMouseMove}
        onmouseleave={handleMouseLeave}
        role="button"
        tabindex="0"
        class="w-full text-left cursor-pointer"
        style="perspective: 1000px;"
    >
        <div 
            class="relative poster-aspect rounded-xl overflow-hidden bg-surface border border-border-subtle transition-all duration-150 card-hover"
            style="transform: rotateX({tiltX}deg) rotateY({tiltY}deg); transform-style: preserve-3d;"
        >
            {#if item.cover_url}
                <img 
                    src={normalizeUrl(item.cover_url)} 
                    alt={item.title || 'Обложка'} 
                    class="w-full h-full object-cover transition-all duration-200 {isHovered ? 'scale-110' : 'scale-100'}"
                    loading="lazy"
                />
                <div class="absolute inset-0 bg-gradient-to-t from-void via-void/20 to-transparent opacity-70 transition-opacity duration-300 {isHovered ? 'opacity-90' : ''}"></div>
            {:else}
                <div class="w-full h-full flex items-center justify-center bg-surface transition-colors duration-300 {isHovered ? 'bg-surface-hover' : ''}">
                    <ImageIcon size={48} class="text-text-muted/20 transition-all duration-300 {isHovered ? 'scale-110 text-text-muted/30' : ''}" />
                </div>
            {/if}

            {#if (item.rating ?? 0) > 0}
                <div class="absolute top-2.5 right-2.5 flex items-center gap-1 bg-void/80 backdrop-blur-md px-2.5 py-1 rounded-lg border border-border-subtle shadow-lg transition-transform duration-300 {isHovered ? 'scale-105' : ''}">
                    <Star size={12} class="text-warning fill-warning" />
                    <span class="text-xs font-bold text-white">{item.rating}</span>
                </div>
            {/if}

            {#if item.source_url}
                <div class="absolute top-2.5 left-2.5">
                    <div class="bg-accent/90 backdrop-blur-sm p-1.5 rounded-lg shadow-lg transition-transform duration-150 {isHovered ? 'scale-110' : ''}" title="Импортировано">
                        <Sparkles size={12} class="text-white" />
                    </div>
                </div>
            {/if}

            <div class="absolute inset-0 flex flex-col justify-end p-3 opacity-0 group-hover:opacity-100 transition-all duration-150">
                <div class="transform translate-y-4 group-hover:translate-y-0 transition-transform duration-150">
                    <div class="flex gap-2 mb-2">
                        <button
                            onclick={handleEditClick}
                            class="flex-1 py-2 text-xs font-medium bg-white/15 backdrop-blur-md hover:bg-white/25 text-white rounded-lg transition-all duration-200 border border-white/10 flex items-center justify-center gap-1.5"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/></svg>
                            Редактировать
                        </button>
                    </div>
                </div>
            </div>

            <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-250 pointer-events-none">
                <div class="absolute inset-0 bg-gradient-to-tr from-transparent via-white/5 to-transparent transform -translate-x-full group-hover:translate-x-full transition-transform duration-500"></div>
            </div>
        </div>

        <div class="mt-3 px-0.5">
            <h3 class="font-semibold text-sm text-text-primary line-clamp-2 leading-snug group-hover:text-accent transition-colors duration-150">
                {item.title || 'Без названия'}
            </h3>
            {#if item.comment}
                <p class="text-xs text-text-muted mt-1 line-clamp-1 transition-colors duration-150 group-hover:text-text-secondary">{item.comment}</p>
            {/if}
            {#if item.tags && item.tags.length > 0}
                <div class="flex flex-wrap gap-1 mt-2 min-w-0">
                    {#each item.tags as tag}
                        <span
                            class="px-1.5 py-0.5 rounded-md bg-surface-raised border border-border-subtle
                                text-[10px] text-text-muted max-w-full truncate"
                        >
                            {tag}
                        </span>
                    {/each}
                </div>
            {/if}
        </div>
    </div>

    <button
        onclick={handleDeleteClick}
        class="absolute -top-2 -right-2 w-8 h-8 rounded-full bg-surface-raised border border-border-subtle flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-100 hover:bg-danger-soft hover:border-danger/30 hover:text-danger z-10 shadow-lg hover:scale-110"
        title="Удалить"
    >
        {#if deleteConfirmId === item.id}
            <svg xmlns="http://www.w3.org/2000/svg" width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-danger"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
        {:else}
            <svg xmlns="http://www.w3.org/2000/svg" width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-muted"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
        {/if}
    </button>
</div>
