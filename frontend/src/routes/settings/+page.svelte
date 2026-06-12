<script lang="ts">
    import { 
        Trash2, AlertTriangle, RotateCcw, Info, Database, 
        Check, Link, ExternalLink, Download, Upload, X
    } from 'lucide-svelte';
    import { fade, fly, scale } from 'svelte/transition';
    import { quintOut, backOut } from 'svelte/easing';

    const API_BASE = 'http://localhost:8000';

    let activeTab = $state('data');
    let confirmModal = $state<{ show: boolean, type: 'local' | 'db' | null }>({ show: false, type: null });
    
    let toast = $state<{ show: boolean, message: string, type: 'success' | 'error' }>({ show: false, message: '', type: 'success' });

    // svelte-ignore non_reactive_update
    let fileInput: HTMLInputElement;

    const STORAGE_KEYS = ['sidebar-item-order', 'sidebar-last-tab'];

    const tabs = [
        { id: 'data', label: 'Данные', icon: Database },
        { id: 'sites', label: 'Сайты', icon: Link },
        { id: 'about', label: 'О приложении', icon: Info }
    ];

    const supportedSites = [
        'https://www.chitai-gorod.ru/', 'https://www.kinopoisk.ru/', 'https://www.litres.ru/',
        'https://remanga.org/', 'https://реманга.орг/', 'https://shikimori.io/',
        'https://store.steampowered.com/', 'https://mangalib.me/', 'https://mangalib.org/',
        'https://ranobelib.me/', 'https://hentailib.me/', 'https://anilib.me/'
    ];

    function showToast(message: string, type: 'success' | 'error' = 'success', duration = 3000) {
        toast = { show: true, message, type };
        setTimeout(() => toast.show = false, duration);
    }

    function clearAllLocalData() {
        try {
            STORAGE_KEYS.forEach(key => localStorage.removeItem(key));
            showToast('Локальные настройки очищены');
            confirmModal = { show: false, type: null };
        } catch {
            showToast('Ошибка при очистке локальных данных', 'error');
        }
    }

    async function clearDatabase() {
        try {
            const res = await fetch(`${API_BASE}/api/clear-db`, { method: 'POST' });
            if (!res.ok) throw new Error('Ошибка сервера');
            showToast('База данных успешно очищена');
            confirmModal = { show: false, type: null };
        } catch (error) {
            showToast('Не удалось очистить базу данных', 'error');
        }
    }

    async function handleExport() {
        try {
            const res = await fetch(`${API_BASE}/api/export-db`, { method: 'GET' });
            if (!res.ok) throw new Error('Ошибка сервера');
            
            const blob = await res.blob();

            if ('showSaveFilePicker' in window) {
                try {
                    const fileHandle = await (window as any).showSaveFilePicker({
                        suggestedName: 'saveitall_backup.json',
                        types: [{
                            description: 'Файл базы данных JSON',
                            accept: { 'application/json': ['.json'] },
                        }],
                    });
                    
                    const writable = await fileHandle.createWritable();
                    await writable.write(blob);
                    await writable.close();
                    
                    showToast('База данных успешно сохранена');
                    return;
                } catch (err: any) {
                    if (err.name === 'AbortError') return;
                    console.error('Ошибка при сохранении:', err);
                }
            }

            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'saveitall_backup.json';
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
            
            showToast('Файл скачан (проверьте папку Загрузки)');
        } catch (error) {
            showToast('Ошибка экспорта базы данных', 'error');
        }
    }

    async function handleFileSelect(event: Event) {
        const target = event.target as HTMLInputElement;
        if (!target.files || target.files.length === 0) return;

        const file = target.files[0];
        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await fetch(`${API_BASE}/api/import-db`, {
                method: 'POST',
                body: formData
            });
            if (!res.ok) throw new Error('Ошибка сервера');
            showToast('Данные успешно импортированы');
        } catch (error) {
            showToast('Ошибка импорта базы данных', 'error');
        } finally {
            // Сбрасываем input, чтобы можно было выбрать тот же файл снова
            target.value = '';
        }
    }

    function confirmAction() {
        if (confirmModal.type === 'local') clearAllLocalData();
        if (confirmModal.type === 'db') clearDatabase();
    }
</script>

<div class="max-w-3xl mx-auto animate-fade-in-up">
    <div class="mb-8 text-center sm:text-left">
        <h1 class="text-3xl font-bold text-gradient mb-2">Настройки</h1>
        <p class="text-text-secondary text-sm">Управление данными, сервером и персонализация</p>
    </div>

    <!-- Вкладки -->
    <div class="flex overflow-x-auto gap-2 mb-6 p-1 bg-surface/30 rounded-2xl border border-border-subtle hide-scrollbar">
        {#each tabs as tab}
            <button
                onclick={() => activeTab = tab.id}
                class="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all whitespace-nowrap
                {activeTab === tab.id ? 'bg-surface-raised border border-border-subtle text-text-primary shadow-sm' : 'text-text-muted hover:text-text-secondary hover:bg-surface/50'}"
            >
                <svelte:component this={tab.icon} size={16} />
                {tab.label}
            </button>
        {/each}
    </div>

    <div class="glass-panel rounded-2xl p-6 min-h-[400px]">
        
        <!-- Вкладка: Данные -->
        {#if activeTab === 'data'}
            <div in:fade={{ duration: 200 }} class="space-y-8">
                <!-- Локальные данные -->
                <div class="space-y-4">
                    <h2 class="text-lg font-semibold text-text-primary flex items-center gap-2">
                        <RotateCcw size={18} class="text-accent" /> Локальный кэш
                    </h2>
                    <button
                        onclick={() => confirmModal = { show: true, type: 'local' }}
                        class="w-full flex items-center justify-between p-4 rounded-xl bg-surface/50 border border-border-subtle hover:bg-surface-hover transition-all group"
                    >
                        <div class="flex items-center gap-3">
                            <div class="w-8 h-8 rounded-lg bg-surface-raised flex items-center justify-center">
                                <Trash2 size={16} class="text-text-muted group-hover:text-text-primary transition-colors" />
                            </div>
                            <div class="text-left">
                                <p class="text-sm font-medium text-text-primary">Очистить локальные настройки</p>
                                <p class="text-xs text-text-muted">Сброс порядка вкладок и запомненной категории</p>
                            </div>
                        </div>
                    </button>
                </div>

                <hr class="border-border-subtle" />

                <!-- Импорт / Экспорт -->
                <div class="space-y-4">
                    <h2 class="text-lg font-semibold text-text-primary flex items-center gap-2">
                        <Database size={18} class="text-accent" /> Резервная копия БД
                    </h2>
                    
                    <div class="grid gap-4 sm:grid-cols-2">
                        <!-- Скрытый инпут для выбора файла -->
                        <input type="file" accept=".json" class="hidden" bind:this={fileInput} onchange={handleFileSelect} />
                        
                        <button onclick={() => fileInput.click()} class="p-4 rounded-xl bg-surface/50 border border-border-subtle hover:bg-surface-hover hover:border-accent/50 transition-all flex flex-col items-center justify-center gap-3 group h-32">
                            <div class="w-10 h-10 rounded-full bg-surface-raised border border-border-subtle flex items-center justify-center group-hover:scale-110 transition-transform">
                                <Upload size={20} class="text-text-primary group-hover:text-accent transition-colors" />
                            </div>
                            <div class="text-center">
                                <p class="text-sm font-medium text-text-primary">Импорт БД</p>
                                <p class="text-xs text-text-muted mt-1">Загрузить из .json файла</p>
                            </div>
                        </button>

                        <button onclick={handleExport} class="p-4 rounded-xl bg-surface/50 border border-border-subtle hover:bg-surface-hover hover:border-accent/50 transition-all flex flex-col items-center justify-center gap-3 group h-32">
                            <div class="w-10 h-10 rounded-full bg-surface-raised border border-border-subtle flex items-center justify-center group-hover:scale-110 transition-transform">
                                <Download size={20} class="text-text-primary group-hover:text-accent transition-colors" />
                            </div>
                            <div class="text-center">
                                <p class="text-sm font-medium text-text-primary">Экспорт БД</p>
                                <p class="text-xs text-text-muted mt-1">Сохранить как .json файл</p>
                            </div>
                        </button>
                    </div>
                </div>

                <hr class="border-border-subtle" />

                <!-- Очистка БД -->
                <div class="space-y-4">
                    <h2 class="text-lg font-semibold text-danger flex items-center gap-2">
                        <AlertTriangle size={18} /> Опасная зона
                    </h2>
                    <button
                        onclick={() => confirmModal = { show: true, type: 'db' }}
                        class="w-full flex items-center justify-between p-4 rounded-xl bg-danger-soft/50 border border-danger/20 hover:bg-danger-soft transition-all group"
                    >
                        <div class="flex items-center gap-3">
                            <div class="w-8 h-8 rounded-lg bg-danger/10 flex items-center justify-center group-hover:bg-danger/20 transition-colors">
                                <Trash2 size={16} class="text-danger" />
                            </div>
                            <div class="text-left">
                                <p class="text-sm font-medium text-danger">Очистить всю базу данных</p>
                                <p class="text-xs text-danger/70">Удалит абсолютно все сохраненные элементы. Действие необратимо.</p>
                            </div>
                        </div>
                    </button>
                </div>
            </div>
        {/if}

        {#if activeTab === 'sites'}
            <div in:fade={{ duration: 200 }} class="space-y-4">
                <p class="text-sm text-text-secondary mb-4">Список сайтов, с которых поддерживается автоматический импорт данных:</p>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {#each supportedSites as site}
                        <a href={site} target="_blank" rel="noopener noreferrer" class="flex items-center justify-between p-3 rounded-xl bg-surface/50 border border-border-subtle hover:border-accent/50 hover:bg-surface-hover transition-all group">
                            <span class="text-sm text-text-primary truncate">{site.replace('https://', '').replace('www.', '')}</span>
                            <ExternalLink size={14} class="text-text-muted group-hover:text-accent transition-colors" />
                        </a>
                    {/each}
                </div>
            </div>
        {/if}

        {#if activeTab === 'about'}
            <div in:fade={{ duration: 200 }} class="flex flex-col items-center justify-center py-8 text-center space-y-6">
                <div class="w-20 h-20 rounded-2xl accent-gradient flex items-center justify-center shadow-lg shadow-accent/20">
                    <Database size={40} class="text-white" />
                </div>
                <div>
                    <h2 class="text-2xl font-bold text-text-primary">Save It All</h2>
                    <p class="text-sm text-text-muted mt-1">Версия 0.0.1</p>
                </div>
                <p class="text-sm text-text-secondary max-w-md leading-relaxed">
                    Персональный локальный трекер медиа-контента. Отслеживайте игры, аниме, фильмы, мангу, книги и ранобэ в одном удобном месте. Никакой привязки к облаку, все данные хранятся у вас.
                </p>
                <a 
                    href="https://github.com/Aetorny/SaveItAll" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    class="flex items-center gap-2 px-6 py-3 bg-surface-raised border border-border-subtle rounded-xl hover:bg-surface-hover hover:border-text-muted transition-all"
                >
                    <ExternalLink size={20} class="text-text-primary" />
                    <span class="text-sm font-medium text-text-primary">Исходный код на GitHub</span>
                </a>
            </div>
        {/if}
    </div>
</div>

{#if confirmModal.show}
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4" transition:fade={{ duration: 200 }}>
        <div class="absolute inset-0 modal-overlay" onclick={() => confirmModal = {show: false, type: null}}></div>
        <div 
            class="relative w-full max-w-md glass-panel-strong rounded-2xl p-6 shadow-2xl"
            transition:scale={{ duration: 350, easing: backOut, start: 0.9 }}
        >
            <div class="flex items-center gap-3 mb-4">
                <div class="w-12 h-12 rounded-full {confirmModal.type === 'db' ? 'bg-danger/20 border-danger/30' : 'bg-warning-soft border-warning/20'} border flex items-center justify-center animate-bounce-subtle">
                    <AlertTriangle size={24} class={confirmModal.type === 'db' ? 'text-danger' : 'text-warning'} />
                </div>
                <div>
                    <h3 class="text-lg font-bold text-text-primary">Подтвердите действие</h3>
                    <p class="text-xs text-text-muted">Это действие нельзя отменить</p>
                </div>
            </div>
            
            <p class="text-text-secondary text-sm mb-6 leading-relaxed">
                {#if confirmModal.type === 'local'}
                    Все локальные настройки будут удалены, включая порядок вкладок и последнюю выбранную категорию. База данных затронута не будет.
                {:else if confirmModal.type === 'db'}
                    <strong class="text-danger">Внимание!</strong> Вы собираетесь полностью очистить базу данных. Все ваши сохранения, оценки и заметки будут безвозвратно удалены.
                {/if}
            </p>

            <div class="flex gap-3">
                <button 
                    onclick={() => confirmModal = {show: false, type: null}}
                    class="flex-1 px-4 py-2.5 bg-surface border border-border-subtle text-text-secondary rounded-xl hover:bg-surface-hover transition-all duration-200 text-sm font-medium"
                >
                    Отмена
                </button>
                <button 
                    onclick={confirmAction}
                    class="flex-1 px-4 py-2.5 text-white rounded-xl transition-all duration-200 text-sm font-medium flex items-center justify-center gap-2 group {confirmModal.type === 'db' ? 'bg-danger hover:bg-danger/80' : 'bg-warning hover:bg-warning/80'}"
                >
                    <Trash2 size={16} class="group-hover:scale-110 transition-transform" />
                    Очистить
                </button>
            </div>
        </div>
    </div>
{/if}

<!-- Toast уведомления -->
{#if toast.show}
    <div 
        class="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 px-6 py-3 rounded-xl shadow-lg flex items-center gap-3 border
        {toast.type === 'error' ? 'bg-danger-soft text-danger border-danger/20' : 'bg-success-soft text-success border-success/20'}"
        transition:fly={{ y: 20, duration: 400, easing: quintOut }}
    >
        {#if toast.type === 'success'}
            <Check size={18} />
        {:else}
            <X size={18} />
        {/if}
        <span class="text-sm font-medium">{toast.message}</span>
    </div>
{/if}