<script lang="ts">
    import { Trash2, AlertTriangle, RotateCcw, Info } from 'lucide-svelte';
    import { fade, fly } from 'svelte/transition';

    let showResetConfirm = false;
    let resetSuccess = false;

    const STORAGE_KEYS = ['sidebar-item-order', 'sidebar-last-tab'];

    function resetOrder() {
        try {
            localStorage.removeItem('sidebar-item-order');
            resetSuccess = true;
            showResetConfirm = false;
            setTimeout(() => resetSuccess = false, 3000);
        } catch {
            // ignore
        }
    }

    function clearAllData() {
        try {
            STORAGE_KEYS.forEach(key => localStorage.removeItem(key));
            resetSuccess = true;
            showResetConfirm = false;
            setTimeout(() => resetSuccess = false, 3000);
        } catch {
            // ignore
        }
    }
</script>

<div class="max-w-2xl animate-fade-in-up">
    <h1 class="text-3xl font-bold text-text-primary mb-2">Настройки</h1>
    <p class="text-text-secondary text-sm mb-8">Управление данными приложения</p>

    <div class="space-y-6">
        <!-- About section -->
        <div class="glass-panel rounded-2xl p-6">
            <div class="flex items-center gap-3 mb-4">
                <div class="w-10 h-10 rounded-xl accent-gradient flex items-center justify-center">
                    <Info size={20} class="text-white" />
                </div>
                <div>
                    <h2 class="font-semibold text-text-primary">О приложении</h2>
                    <p class="text-xs text-text-muted">Media Tracker v0.0.1</p>
                </div>
            </div>
            <p class="text-sm text-text-secondary leading-relaxed">
                Персональный трекер медиа-контента. Отслеживайте игры, аниме, фильмы, мангу, книги и ранобэ в одном месте.
            </p>
        </div>

        <!-- Data management -->
        <div class="glass-panel rounded-2xl p-6">
            <div class="flex items-center gap-3 mb-4">
                <div class="w-10 h-10 rounded-xl bg-surface border border-border-subtle flex items-center justify-center">
                    <RotateCcw size={20} class="text-text-secondary" />
                </div>
                <div>
                    <h2 class="font-semibold text-text-primary">Управление данными</h2>
                    <p class="text-xs text-text-muted">Сброс настроек и кэша</p>
                </div>
            </div>

            <div class="space-y-3">
                <button
                    on:click={() => showResetConfirm = true}
                    class="w-full flex items-center justify-between p-4 rounded-xl bg-surface/50 border border-border-subtle hover:bg-surface hover:border-border-hover transition-all group"
                >
                    <div class="flex items-center gap-3">
                        <RotateCcw size={18} class="text-text-muted group-hover:text-text-secondary transition-colors" />
                        <div class="text-left">
                            <p class="text-sm font-medium text-text-primary">Сбросить порядок вкладок</p>
                            <p class="text-xs text-text-muted">Вернуть боковую панель в исходное состояние</p>
                        </div>
                    </div>
                </button>

                <button
                    on:click={() => showResetConfirm = true}
                    class="w-full flex items-center justify-between p-4 rounded-xl bg-surface/50 border border-border-subtle hover:bg-danger-soft hover:border-danger/20 transition-all group"
                >
                    <div class="flex items-center gap-3">
                        <Trash2 size={18} class="text-text-muted group-hover:text-danger transition-colors" />
                        <div class="text-left">
                            <p class="text-sm font-medium text-text-primary group-hover:text-danger transition-colors">Очистить все локальные данные</p>
                            <p class="text-xs text-text-muted">Удалить порядок вкладок и последнюю категорию</p>
                        </div>
                    </div>
                </button>
            </div>
        </div>
    </div>
</div>

{#if showResetConfirm}
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4" transition:fade={{ duration: 200 }}>
        <div class="absolute inset-0 bg-void/80 backdrop-blur-xl" on:click={() => showResetConfirm = false}></div>
        <div 
            class="relative w-full max-w-md glass-panel-strong rounded-2xl p-6 shadow-2xl"
            transition:fly={{ y: 20, duration: 300 }}
        >
            <div class="flex items-center gap-3 mb-4">
                <div class="w-10 h-10 rounded-full bg-warning-soft border border-warning/20 flex items-center justify-center">
                    <AlertTriangle size={20} class="text-warning" />
                </div>
                <h3 class="text-lg font-bold text-text-primary">Подтвердите действие</h3>
            </div>
            <p class="text-text-secondary text-sm mb-6">
                Это действие нельзя отменить. Все локальные настройки будут удалены.
            </p>
            <div class="flex gap-3">
                <button 
                    on:click={() => showResetConfirm = false}
                    class="flex-1 px-4 py-2.5 bg-surface border border-border-subtle text-text-secondary rounded-xl hover:bg-surface-hover transition-all text-sm font-medium"
                >
                    Отмена
                </button>
                <button 
                    on:click={clearAllData}
                    class="flex-1 px-4 py-2.5 bg-danger text-white rounded-xl hover:bg-danger/80 transition-all text-sm font-medium"
                >
                    Очистить
                </button>
            </div>
        </div>
    </div>
{/if}

{#if resetSuccess}
    <div 
        class="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 px-6 py-3 bg-success-soft border border-success/20 text-success rounded-xl shadow-lg flex items-center gap-2"
        transition:fly={{ y: 20, duration: 300 }}
    >
        <RotateCcw size={16} />
        <span class="text-sm font-medium">Настройки сброшены</span>
    </div>
{/if}
