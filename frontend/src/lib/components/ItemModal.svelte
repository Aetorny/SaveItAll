<script lang="ts">
    import { X, Sparkles, Loader2, Link2, AlertCircle, Check, Plus, Tag } from 'lucide-svelte';
    import { fade, scale, fly } from 'svelte/transition';
    import { backOut } from 'svelte/easing';
    import RatingSlider from './RatingSlider.svelte';
    import type { Importer } from '$lib/index';
    import { createEventDispatcher } from 'svelte';

    interface Props {
        show: boolean;
        editingId: number | null;
        formData: {
            title: string;
            source_url: string;
            cover_url: string;
            description: string;
            rating: number;
            comment: string;
        };
        itemTags?: string[];
        allTags?: string[];
        sourceUrl: string;
        importer: Importer | null;
        importError: string;
        importState: 'idle' | 'loading';
    }

    let { 
        show, 
        editingId, 
        formData = $bindable(), 
        itemTags = $bindable([]),
        allTags = [],
        sourceUrl = $bindable(), 
        importer, 
        importError, 
        importState 
    }: Props = $props();

    const dispatch = createEventDispatcher<{
        close: void;
        submit: void;
        import: void;
        sourceUrlChange: string;
        createTag: string;
        toggleTag: string;
    }>();

    let isNew = $derived(!editingId);
    let hasImporter = $derived(!!importer && !!sourceUrl);
    let titleRequired = $derived(!hasImporter);
    let modalRef = $state<HTMLDivElement | null>(null);
    let newTagInput = $state('');

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

    function handleToggleTag(tag: string) {
        dispatch('toggleTag', tag);
    }

    function createTagFromModal() {
        const trimmed = newTagInput.trim();
        if (!trimmed) return;
        dispatch('createTag', trimmed);
        dispatch('toggleTag', trimmed);
        newTagInput = '';
    }

    function handleKeydown(e: KeyboardEvent) {
        if (e.key === 'Escape') {
            handleClose();
        }
    }

    $effect(() => {
        if (show) {
            setTimeout(() => {
                const firstInput = modalRef?.querySelector('input, textarea, select');
                if (firstInput) {
                    (firstInput as HTMLElement).focus();
                }
            }, 100);
        }
    });
</script>

{#if show}
    <div 
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        transition:fade={{ duration: 150 }}
        role="dialog"
        aria-modal="true"
    >
        <div 
            class="absolute inset-0 modal-overlay"
            onclick={handleClose}
        ></div>

        <!-- svelte-ignore a11y_no_static_element_interactions -->
        <div 
            bind:this={modalRef}
            class="relative w-full max-w-5xl glass-panel-strong rounded-2xl shadow-2xl max-h-full overflow-y-auto custom-scrollbar"
            transition:scale={{ duration: 200, easing: backOut, start: 1 }}
            onkeydown={handleKeydown}
        >
            <div class="p-6 md:p-6">
                <div class="flex items-center justify-between mb-3">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-xl {isNew ? 'bg-accent/10 border border-accent/20' : 'bg-surface border border-border-subtle'} flex items-center justify-center">
                            {#if isNew}
                                <Sparkles size={18} class="text-accent" />
                            {:else}
                                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-text-secondary"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/></svg>
                            {/if}
                        </div>
                        <h2 class="text-xl font-bold text-text-primary">
                            {isNew ? 'Добавить элемент' : 'Редактировать'}
                        </h2>
                    </div>
                    <button 
                        onclick={handleClose}
                        class="w-9 h-9 rounded-xl hover:bg-surface flex items-center justify-center text-text-muted hover:text-text-primary transition-all duration-200 hover:rotate-90"
                        aria-label="Закрыть"
                    >
                        <X size={18} />
                    </button>
                </div>

                <form onsubmit={handleSubmit} class="space-y-5">
                    <div class="space-y-3" in:fly={{ y: 10, duration: 150, delay: 50 }}>
                        <label class="block text-xs font-semibold text-text-muted uppercase tracking-wider flex items-center gap-2" for="url">
                            <Link2 size={12} />
                            Ссылка на источник
                        </label>
                        <div class="flex gap-2">
                            <input 
                                id="url" 
                                type="url" 
                                value={sourceUrl}
                                oninput={handleSourceUrlInput}
                                class="flex-1 bg-surface border border-border-subtle text-text-primary rounded-xl px-4 py-2.5 text-sm placeholder:text-text-muted focus:border-accent focus:outline-none transition-all duration-200"
                                placeholder="https://..."
                            />
                            <button 
                                type="button" 
                                onclick={handleImport}
                                disabled={!importer || importState === 'loading'}
                                class="px-4 py-2.5 bg-success-soft border border-success/20 text-success rounded-xl hover:bg-success hover:text-white transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2 text-sm font-medium shrink-0 group"
                            >
                                {#if importState === 'loading'}
                                    <Loader2 size={16} class="animate-spin" />
                                {:else}
                                    <Sparkles size={16} class="group-hover:scale-110 transition-transform" />
                                {/if}
                                Импорт
                            </button>
                        </div>

                        {#if importer}
                            <div class="flex items-center gap-2 text-xs text-success bg-success-soft/50 px-3 py-2 rounded-lg" in:fly={{ y: 5, duration: 200 }}>
                                <Check size={12} />
                                <span>Поддерживается импорт из <span class="font-semibold">{importer.name}</span></span>
                            </div>
                        {:else if sourceUrl}
                            <div class="flex items-center gap-2 text-xs text-text-muted bg-surface px-3 py-2 rounded-lg">
                                <AlertCircle size={12} />
                                <span>Вставьте ссылку на поддерживаемый сайт для автоматического импорта</span>
                            </div>
                        {/if}

                        {#if importError}
                            <div class="flex items-center gap-2 text-xs text-danger bg-danger-soft px-3 py-2 rounded-lg animate-shake" in:fly={{ y: 5, duration: 200 }}>
                                <AlertCircle size={12} />
                                <span>{importError}</span>
                            </div>
                        {/if}
                    </div>

                    <div class="space-y-3" in:fly={{ y: 10, duration: 150, delay: 75 }}>
                        <label class="block text-xs font-semibold text-text-muted uppercase tracking-wider flex items-center gap-2">
                            <Tag size={12} />
                            Теги
                        </label>
                        <div class="flex flex-wrap gap-2">
                            {#each allTags as tag}
                                <button
                                    type="button"
                                    onclick={() => handleToggleTag(tag)}
                                    class="px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-100 border {itemTags.includes(tag) ? 'bg-accent text-white border-accent shadow-lg shadow-accent-glow' : 'bg-surface text-text-secondary border-border-subtle hover:bg-surface-hover'}"
                                >
                                    {tag}
                                </button>
                            {/each}
                        </div>
                        <div class="flex gap-2">
                            <input 
                                type="text" 
                                bind:value={newTagInput}
                                placeholder="Новый тег..."
                                class="flex-1 bg-surface border border-border-subtle text-text-primary rounded-xl px-4 py-2 text-sm placeholder:text-text-muted focus:border-accent focus:outline-none"
                                onkeydown={(e) => e.key === 'Enter' && (e.preventDefault(), createTagFromModal())}
                            />
                            <button 
                                type="button"
                                onclick={createTagFromModal}
                                class="px-4 py-2 bg-surface-raised border border-border-subtle text-text-primary rounded-xl hover:bg-surface-hover transition-all text-sm"
                            >
                                <Plus size={16} />
                            </button>
                        </div>
                    </div>

                    <div class="space-y-3" in:fly={{ y: 10, duration: 150, delay: 100 }}>
                        <label class="block text-xs font-semibold text-text-muted uppercase tracking-wider flex items-center gap-2" for="title">
                            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 7V4h16v3"/><path d="M9 20h6"/><path d="M12 4v16"/></svg>
                            Название {#if titleRequired}<span class="text-danger">*</span>{/if}
                        </label>
                        <input 
                            id="title" 
                            type="text" 
                            bind:value={formData.title} 
                            required={titleRequired}
                            class="w-full bg-surface border border-border-subtle text-text-primary rounded-xl px-4 py-2.5 text-sm placeholder:text-text-muted focus:border-accent focus:outline-none transition-all duration-200"
                            placeholder="Название медиа..."
                        />
                    </div>

                    <div class="space-y-3" in:fly={{ y: 10, duration: 150, delay: 150 }}>
                        <label class="block text-xs font-semibold text-text-muted uppercase tracking-wider flex items-center gap-2" for="cover">
                            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></svg>
                            Ссылка на обложку
                        </label>
                        <input 
                            id="cover" 
                            type="url" 
                            bind:value={formData.cover_url} 
                            class="w-full bg-surface border border-border-subtle text-text-primary rounded-xl px-4 py-2.5 text-sm placeholder:text-text-muted focus:border-accent focus:outline-none transition-all duration-200"
                            placeholder="https://..."
                        />
                    </div>

                    <div class="space-y-3" in:fly={{ y: 10, duration: 150, delay: 200 }}>
                        <label class="block text-xs font-semibold text-text-muted uppercase tracking-wider flex items-center gap-2" for="desc">
                            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" x2="8" y1="13" y2="13"/><line x1="16" x2="8" y1="17" y2="17"/><line x1="10" x2="8" y1="9" y2="9"/></svg>
                            Описание
                        </label>
                        <textarea 
                            id="desc" 
                            bind:value={formData.description} 
                            class="w-full bg-surface border border-border-subtle text-text-primary rounded-xl px-4 py-2.5 text-sm placeholder:text-text-muted focus:border-accent focus:outline-none resize-none transition-all duration-200"
                            rows="2"
                            placeholder="Краткое описание..."
                        ></textarea>
                    </div>

                    <div in:fly={{ y: 10, duration: 150, delay: 250 }}>
                        <RatingSlider bind:value={formData.rating} />
                    </div>

                    <div class="space-y-3" in:fly={{ y: 10, duration: 150, delay: 300 }}>
                        <label class="block text-xs font-semibold text-text-muted uppercase tracking-wider flex items-center gap-2" for="comment">
                            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                            Личное впечатление
                        </label>
                        <textarea 
                            id="comment" 
                            bind:value={formData.comment} 
                            class="w-full bg-surface border border-border-subtle text-text-primary rounded-xl px-4 py-2.5 text-sm placeholder:text-text-muted focus:border-accent focus:outline-none resize-none transition-all duration-200"
                            rows="6"
                            placeholder="Ваши мысли об этом..."
                        ></textarea>
                    </div>

                    <div class="flex gap-3 pt-4 border-t border-border-subtle" in:fly={{ y: 10, duration: 150, delay: 350 }}>
                        <button 
                            type="button" 
                            onclick={handleClose}
                            class="flex-1 px-4 py-2.5 bg-surface border border-border-subtle text-text-secondary rounded-xl hover:bg-surface-hover hover:text-text-primary transition-all duration-200 text-sm font-medium"
                        >
                            Отмена
                        </button>
                        <button 
                            type="submit"
                            class="flex-1 px-4 py-2.5 bg-accent text-white rounded-xl hover:bg-accent-hover transition-all duration-100 shadow-lg shadow-accent-glow hover:shadow-xl text-sm font-medium active:scale-95 flex items-center justify-center gap-2 group"
                        >
                            <Check size={16} class="group-hover:scale-110 transition-transform" />
                            {isNew ? 'Добавить' : 'Сохранить изменения'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
{/if}
