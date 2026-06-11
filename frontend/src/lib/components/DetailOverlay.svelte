<script lang="ts">
    import { X, Star, ExternalLink, Trash2, Edit3, Calendar, Link2 } from 'lucide-svelte';
    import { fade, scale, fly } from 'svelte/transition';
    import { quintOut, backOut } from 'svelte/easing';
    import { createEventDispatcher } from 'svelte';

    interface Props {
        item: {
            id: number;
            title?: string;
            source_url?: string;
            cover_url?: string;
            description?: string;
            rating?: number;
            comment?: string;
        } | null;
        deleteConfirmId?: number | null;
    }

    let { item, deleteConfirmId = null }: Props = $props();

    type ItemType = NonNullable<typeof item>;

    const dispatch = createEventDispatcher<{
        close: void;
        edit: ItemType;
        delete: number;
    }>();

    let imageLoaded = $state(false);
    let imageError = $state(false);

    function normalizeUrl(u: string | null | undefined) {
        if (!u) return u;
        if (u.startsWith('//')) return 'https:' + u;
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

    function formatDate(dateStr: string | undefined) {
        if (!dateStr) return null;
        try {
            const date = new Date(dateStr);
            return date.toLocaleDateString('ru-RU', { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
            });
        } catch {
            return null;
        }
    }
</script>


{#if item}
    <div
        class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-8 overflow-hidden"
        transition:fade={{ duration: 250 }}
        role="dialog"
        aria-modal="true"
        aria-labelledby="detail-title"
    >
        <div 
            class="absolute inset-0 modal-overlay"
            onclick={handleClose}
        ></div>

        <div
            class="relative w-full max-w-[95vw] xl:max-w-6xl max-h-[calc(100vh-2rem)] glass-panel-strong rounded-2xl overflow-hidden shadow-2xl animate-scale-in flex flex-col"
            transition:scale={{ duration: 400, easing: backOut, start: 0.9 }}
        >
            <button 
                onclick={handleClose}
                class="absolute top-4 right-4 z-20 w-10 h-10 rounded-full bg-void/60 backdrop-blur-md border border-border-subtle flex items-center justify-center text-text-secondary hover:text-white hover:bg-void/90 transition-all duration-200 hover:scale-110 shadow-lg"
                aria-label="Закрыть"
            >
                <X size={20} />
            </button>

            <div class="flex flex-col md:flex-row min-h-0">
                <div class="md:w-80 shrink-0 relative bg-surface">
                    {#if item.cover_url && !imageError}
                        <img 
                            src={normalizeUrl(item.cover_url)} 
                            alt={item.title || 'Обложка'}
                            class="w-full h-72 md:h-full object-cover transition-opacity duration-500 {imageLoaded ? 'opacity-100' : 'opacity-0'}"
                            loading="lazy"
                            onload={() => imageLoaded = true}
                            onerror={() => imageError = true}
                        />
                        {#if !imageLoaded}
                            <div class="absolute inset-0 flex items-center justify-center">
                                <div class="w-12 h-12 rounded-full border-2 border-accent/30 border-t-accent animate-spin"></div>
                            </div>
                        {/if}
                        <div class="absolute inset-0 bg-gradient-to-t from-void via-void/30 to-transparent md:bg-gradient-to-r"></div>
                    {:else}
                        <div class="w-full h-72 md:h-full bg-surface flex flex-col items-center justify-center gap-3">
                            <div class="w-16 h-16 rounded-2xl bg-surface-raised border border-border-subtle flex items-center justify-center">
                                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="text-text-muted/30"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></svg>
                            </div>
                            <span class="text-xs text-text-muted">Нет обложки</span>
                        </div>
                    {/if}
                </div>

                <div class="flex-1 p-6 md:p-8 flex flex-col min-h-0">
                    <div class="flex-1 min-h-0 overflow-y-auto custom-scrollbar pr-2">
                        <h2 
                            id="detail-title"
                            class="text-2xl md:text-3xl font-bold text-text-primary mb-4 leading-tight"
                            in:fly={{ x: 20, duration: 400, delay: 100, easing: quintOut }}
                        >
                            {item.title || 'Без названия'}
                        </h2>

                        <div class="flex flex-wrap items-center gap-2.5 mb-6" in:fly={{ x: 20, duration: 400, delay: 150, easing: quintOut }}>
                            {#if (item.rating ?? 0) > 0}
                                <div class="flex items-center gap-1.5 bg-warning-soft border border-warning/20 px-3 py-1.5 rounded-lg">
                                    <Star size={14} class="text-warning fill-warning" />
                                    <span class="text-sm font-bold text-warning">{item.rating}/10</span>
                                </div>
                            {/if}
                            {#if item.source_url}
                                <a href={item.source_url} target="_blank" rel="noopener" class="flex items-center gap-1.5 text-xs text-accent hover:text-accent-hover transition-colors bg-accent-glow px-3 py-1.5 rounded-lg border border-accent/10 hover:border-accent/30">
                                    <Link2 size={12} />
                                    Источник
                                    <ExternalLink size={10} />
                                </a>
                            {/if}
                        </div>

                        {#if item.description}
                            <div class="mb-6" in:fly={{ x: 20, duration: 400, delay: 200, easing: quintOut }}>
                                <h4 class="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3 flex items-center gap-2">
                                    <span class="w-1 h-1 rounded-full bg-accent"></span>
                                    Описание
                                </h4>
                                <p class="text-text-secondary text-sm leading-relaxed">{item.description}</p>
                            </div>
                        {/if}

                        {#if item.comment}
                            <div class="mb-6" in:fly={{ x: 20, duration: 400, delay: 250, easing: quintOut }}>
                                <h4 class="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3 flex items-center gap-2">
                                    <span class="w-1 h-1 rounded-full bg-success"></span>
                                    Мои заметки
                                </h4>
                                <div class="bg-surface/50 border border-border-subtle rounded-xl p-4 relative">
                                    <div class="absolute -top-2 left-4 w-4 h-4 bg-surface/50 border-l border-t border-border-subtle rotate-45"></div>
                                    <p class="text-text-primary text-sm italic leading-relaxed relative z-10 break-all">
                                        {item.comment}
                                    </p>
                                </div>
                            </div>
                        {/if}
                    </div>

                    <div 
                        class="flex gap-3 pt-4 mt-4 border-t border-border-subtle shrink-0"
                        in:fly={{ y: 20, duration: 400, delay: 300, easing: quintOut }}
                    >
                        <button onclick={handleEdit} class="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-surface-raised border border-border-subtle text-text-primary rounded-xl hover:bg-surface-hover hover:border-border-hover transition-all duration-200 font-medium text-sm group">
                            <Edit3 size={16} class="group-hover:scale-110 transition-transform" />
                            Редактировать
                        </button>
                        <button onclick={handleDelete} class="flex items-center justify-center gap-2 px-5 py-2.5 bg-danger-soft border border-danger/20 text-danger rounded-xl hover:bg-danger hover:text-white transition-all duration-200 font-medium text-sm group" class:animate-shake={deleteConfirmId === item.id}>
                            <Trash2 size={16} class="group-hover:scale-110 transition-transform" />
                            {deleteConfirmId === item.id ? 'Подтвердить' : 'Удалить'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
{/if}

<style>
    .custom-scrollbar {
        scrollbar-width: thin;
        scrollbar-color: rgba(255, 255, 255, 0.12) transparent;
    }
    .custom-scrollbar::-webkit-scrollbar {
        width: 5px;
    }
    .custom-scrollbar::-webkit-scrollbar-track {
        background: transparent;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb {
        background-color: rgba(255, 255, 255, 0.12);
        border-radius: 20px;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb:hover {
        background-color: rgba(255, 255, 255, 0.28);
    }
</style>