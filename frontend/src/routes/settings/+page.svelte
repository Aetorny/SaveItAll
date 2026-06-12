<script lang="ts">
    import { Trash2, AlertTriangle, RotateCcw, Info, Zap, Database, Palette, Check } from 'lucide-svelte';
    import { fade, fly, scale } from 'svelte/transition';
    import { quintOut, backOut } from 'svelte/easing';

    let showResetConfirm = $state(false);
    let resetSuccess = $state(false);
    let activeSection = $state<string | null>(null);

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

    const settingsSections = [
        {
            id: 'about',
            title: 'О приложении',
            subtitle: 'Save It All v0.0.1',
            icon: Info,
            iconBg: 'accent-gradient',
            iconColor: 'text-white',
            description: 'Персональный трекер медиа-контента. Отслеживайте игры, аниме, фильмы, мангу, книги и ранобэ в одном месте.',
        },
        {
            id: 'data',
            title: 'Управление данными',
            subtitle: 'Сброс настроек и кэша',
            icon: Database,
            iconBg: 'bg-surface border border-border-subtle',
            iconColor: 'text-text-secondary',
            description: 'Управление локальными данными приложения.',
        },
        {
            id: 'features',
            title: 'Возможности',
            subtitle: 'Что умеет приложение',
            icon: Zap,
            iconBg: 'bg-warning-soft border border-warning/20',
            iconColor: 'text-warning',
            description: 'Импорт данных с популярных сайтов, drag-and-drop сортировка, оценки и заметки.',
        }
    ];
</script>

<div class="max-w-2xl animate-fade-in-up">
    <div class="mb-8">
        <h1 class="text-3xl font-bold text-gradient mb-2">Настройки</h1>
        <p class="text-text-secondary text-sm">Управление данными и персонализация</p>
    </div>

    <div class="space-y-6">
        {#each settingsSections as section, index}
            <div 
                class="glass-panel rounded-2xl p-6 transition-all duration-300 hover:border-border-hover"
                in:fly={{ y: 20, duration: 400, delay: index * 100, easing: quintOut }}
            >
                <div class="flex items-center gap-3 mb-4">
                    <div class="w-10 h-10 rounded-xl {section.iconBg} flex items-center justify-center transition-transform duration-300 hover:scale-110">
                        <svelte:component this={section.icon} size={20} class={section.iconColor} />
                    </div>
                    <div>
                        <h2 class="font-semibold text-text-primary">{section.title}</h2>
                        <p class="text-xs text-text-muted">{section.subtitle}</p>
                    </div>
                </div>
                <p class="text-sm text-text-secondary leading-relaxed mb-4">{section.description}</p>

                {#if section.id === 'data'}
                    <div class="space-y-3">
                        <button
                            on:click={() => showResetConfirm = true}
                            class="w-full flex items-center justify-between p-4 rounded-xl bg-surface/50 border border-border-subtle hover:bg-surface hover:border-border-hover transition-all duration-200 group"
                        >
                            <div class="flex items-center gap-3">
                                <div class="w-8 h-8 rounded-lg bg-surface-raised border border-border-subtle flex items-center justify-center group-hover:scale-110 transition-transform">
                                    <RotateCcw size={16} class="text-text-muted group-hover:text-text-secondary transition-colors" />
                                </div>
                                <div class="text-left">
                                    <p class="text-sm font-medium text-text-primary">Сбросить порядок вкладок</p>
                                    <p class="text-xs text-text-muted">Вернуть боковую панель в исходное состояние</p>
                                </div>
                            </div>
                            <div class="w-8 h-8 rounded-lg bg-surface-raised border border-border-subtle flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all">
                                <RotateCcw size={14} class="text-text-secondary" />
                            </div>
                        </button>

                        <button
                            on:click={() => showResetConfirm = true}
                            class="w-full flex items-center justify-between p-4 rounded-xl bg-surface/50 border border-border-subtle hover:bg-danger-soft hover:border-danger/20 transition-all duration-200 group"
                        >
                            <div class="flex items-center gap-3">
                                <div class="w-8 h-8 rounded-lg bg-surface-raised border border-border-subtle flex items-center justify-center group-hover:bg-danger/20 transition-colors">
                                    <Trash2 size={16} class="text-text-muted group-hover:text-danger transition-colors" />
                                </div>
                                <div class="text-left">
                                    <p class="text-sm font-medium text-text-primary group-hover:text-danger transition-colors">Очистить все локальные данные</p>
                                    <p class="text-xs text-text-muted">Удалить порядок вкладок и последнюю категорию</p>
                                </div>
                            </div>
                            <div class="w-8 h-8 rounded-lg bg-surface-raised border border-border-subtle flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all group-hover:bg-danger/20">
                                <Trash2 size={14} class="text-danger" />
                            </div>
                        </button>
                    </div>
                {/if}

                {#if section.id === 'features'}
                    <div class="grid grid-cols-2 gap-3">
                        {#each [
                            { label: 'Импорт с сайтов', icon: '✨' },
                            { label: 'Drag & Drop', icon: '📦' },
                            { label: 'Оценки 1-10', icon: '⭐' },
                            { label: 'Заметки', icon: '📝' },
                        ] as feature}
                            <div class="flex items-center gap-2 p-3 rounded-xl bg-surface/50 border border-border-subtle">
                                <span class="text-lg">{feature.icon}</span>
                                <span class="text-sm text-text-secondary">{feature.label}</span>
                            </div>
                        {/each}
                    </div>
                {/if}
            </div>
        {/each}
    </div>
</div>

<!-- Confirmation modal -->
{#if showResetConfirm}
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4" transition:fade={{ duration: 200 }}>
        <div class="absolute inset-0 modal-overlay" on:click={() => showResetConfirm = false}></div>
        <div 
            class="relative w-full max-w-md glass-panel-strong rounded-2xl p-6 shadow-2xl"
            transition:scale={{ duration: 350, easing: backOut, start: 0.9 }}
        >
            <div class="flex items-center gap-3 mb-4">
                <div class="w-12 h-12 rounded-full bg-warning-soft border border-warning/20 flex items-center justify-center animate-bounce-subtle">
                    <AlertTriangle size={24} class="text-warning" />
                </div>
                <div>
                    <h3 class="text-lg font-bold text-text-primary">Подтвердите действие</h3>
                    <p class="text-xs text-text-muted">Это действие нельзя отменить</p>
                </div>
            </div>
            <p class="text-text-secondary text-sm mb-6 leading-relaxed">
                Все локальные настройки будут удалены, включая порядок вкладок и последнюю выбранную категорию. Данные на сервере не затронуты.
            </p>
            <div class="flex gap-3">
                <button 
                    on:click={() => showResetConfirm = false}
                    class="flex-1 px-4 py-2.5 bg-surface border border-border-subtle text-text-secondary rounded-xl hover:bg-surface-hover transition-all duration-200 text-sm font-medium"
                >
                    Отмена
                </button>
                <button 
                    on:click={clearAllData}
                    class="flex-1 px-4 py-2.5 bg-danger text-white rounded-xl hover:bg-danger/80 transition-all duration-200 text-sm font-medium flex items-center justify-center gap-2 group"
                >
                    <Trash2 size={16} class="group-hover:scale-110 transition-transform" />
                    Очистить
                </button>
            </div>
        </div>
    </div>
{/if}

<!-- Success toast -->
{#if resetSuccess}
    <div 
        class="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 px-6 py-3 bg-success-soft border border-success/20 text-success rounded-xl shadow-lg flex items-center gap-2"
        transition:fly={{ y: 20, duration: 400, easing: quintOut }}
    >
        <Check size={16} />
        <span class="text-sm font-medium">Настройки сброшены</span>
    </div>
{/if}
