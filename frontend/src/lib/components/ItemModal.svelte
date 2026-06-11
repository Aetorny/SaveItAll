<script lang="ts">
    import { X, Sparkles, Loader2 } from 'lucide-svelte';
    import { fade, scale } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';
    import RatingSlider from './RatingSlider.svelte';
    import type { Importer } from '$lib/importers';

    export let show: boolean = false;
    export let editingId: number | null = null;
    export let formData: {
        title: string;
        source_url: string;
        cover_url: string;
        description: string;
        rating: number;
        comment: string;
    };
    export let sourceUrl: string = '';
    export let importer: Importer | null = null;
    export let importError: string = '';
    export let importState: 'idle' | 'loading' = 'idle';

    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher<{
        close: void;
        submit: void;
        import: void;
        sourceUrlChange: string;
    }>();

    $: isNew = !editingId;
    $: hasImporter = !!importer && !!sourceUrl;
    $: titleRequired = !hasImporter;

    function handleClose() {
        dispatch('close');
    }

    function handleSubmit() {
        dispatch('submit');
    }

    function handleImport() {
        dispatch('import');
    }

    function handleSourceUrlInput(e: Event) {
        const target = e.target as HTMLInputElement;
        dispatch('sourceUrlChange', target.value);
    }

    function handleBackdropKeydown(e: KeyboardEvent) {
        if (e.key === 'Enter') handleClose();
    }
</script>

{#if show}
    <div 
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        transition:fade={{ duration: 200 }}
    >
        <div 
            class="absolute inset-0 bg-void/80 backdrop-blur-xl"
            on:click={handleClose}
            role="button"
            tabindex="0"
            on:keydown={handleBackdropKeydown}
        ></div>

        <div 
            class="relative w-full max-w-lg glass-panel-strong rounded-2xl shadow-2xl max-h-[90vh] overflow-y-auto scrollbar-thin animate-scale-in"
            transition:scale={{ duration: 300, easing: quintOut, start: 0.95 }}
        >
            <div class="p-6 md:p-8">
                <div class="flex items-center justify-between mb-6">
                    <h2 class="text-xl font-bold text-text-primary">
                        {isNew ? 'Добавить элемент' : 'Редактировать'}
                    </h2>
                    <button 
                        on:click={handleClose}
                        class="w-8 h-8 rounded-lg hover:bg-surface flex items-center justify-center text-text-muted hover:text-text-primary transition-colors"
                    >
                        <X size={18} />
                    </button>
                </div>

                <form on:submit|preventDefault={handleSubmit} class="space-y-5">
                    <!-- Source URL with auto-import -->
                    <div class="space-y-3">
                        <label class="block text-xs font-semibold text-text-muted uppercase tracking-wider" for="url">Ссылка на источник</label>
                        <div class="flex gap-2">
                            <input 
                                id="url" 
                                type="url" 
                                value={sourceUrl}
                                on:input={handleSourceUrlInput}
                                class="flex-1 bg-surface border border-border-subtle text-text-primary rounded-xl px-4 py-2.5 text-sm placeholder:text-text-muted focus:border-accent focus:outline-none"
                                placeholder="https://shikimori.io/animes/..."
                            />
                            <button 
                                type="button" 
                                on:click={handleImport}
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
                            Название {#if titleRequired}<span class="text-danger">*</span>{/if}
                        </label>
                        <input 
                            id="title" 
                            type="text" 
                            bind:value={formData.title} 
                            required={titleRequired}
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

                    <RatingSlider bind:value={formData.rating} />

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
                            on:click={handleClose}
                            class="flex-1 px-4 py-2.5 bg-surface border border-border-subtle text-text-secondary rounded-xl hover:bg-surface-hover hover:text-text-primary transition-all text-sm font-medium"
                        >
                            Отмена
                        </button>
                        <button 
                            type="submit"
                            class="flex-1 px-4 py-2.5 bg-accent text-white rounded-xl hover:bg-accent-hover transition-all shadow-lg shadow-accent-glow text-sm font-medium active:scale-95"
                        >
                            {isNew ? 'Добавить' : 'Сохранить изменения'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
{/if}
