<script lang="ts">
    import { 
        Trash2, AlertTriangle, RotateCcw, Info, Database, 
        Check, Link, ExternalLink, Download, Upload, X, CloudDownload, FileJson, Settings2,
        Gamepad2, Tv, Clapperboard, BookOpen, Book, ScrollText, Film, Music, Heart, Star, Compass, Flame
    } from 'lucide-svelte';
    import { fade, fly, scale } from 'svelte/transition';
    import { quintOut, backOut } from 'svelte/easing';
    import { api } from '$lib/api'

    import { findImporter } from '$lib/index';

    let activeTab = $state('data');
    let confirmModal = $state<{ show: boolean, type: 'local' | 'db' | null }>({ show: false, type: null });
    
    let toast = $state<{ show: boolean, message: string, type: 'success' | 'error' }>({ show: false, message: '', type: 'success' });

    let importSettingsModal = $state<{
        show: boolean;
        fileData: any[] | null;
        selectedCategory: string;
    }>({
        show: false,
        fileData: null,
        selectedCategory: 'auto'
    });

    const categoryOptions = [
        { id: 'auto', label: 'Автоматически (Аниме/Манга/Ранобэ)' },
        { id: 'anime', label: 'Аниме' },
        { id: 'manga', label: 'Манга' },
        { id: 'ranobe', label: 'Ранобэ' },
        { id: 'movies', label: 'Фильмы/Сериалы' },
        { id: 'books', label: 'Книги' },
        { id: 'games', label: 'Игры' },
        { id: 'other', label: 'Другое' }
    ];

    const availableIcons: Record<string, any> = { 
        Gamepad2, Tv, Clapperboard, BookOpen, Book, ScrollText, Film, Music, Heart, Star, Compass, Flame 
    };
    const STORAGE_KEYS = ['sidebar-item-order', 'sidebar-last-tab', 'sidebar-item-custom'];

    // svelte-ignore non_reactive_update
    let fileInput: HTMLInputElement;
    // svelte-ignore non_reactive_update
    let shikimoriInput: HTMLInputElement;

    const tabs = [
        { id: 'data', label: 'Данные', icon: Database },
        { id: 'import', label: 'Импорт', icon: CloudDownload },
        { id: 'categories', label: 'Категории', icon: Settings2 },
        { id: 'sites', label: 'Сайты', icon: Link },
        { id: 'about', label: 'О приложении', icon: Info }
    ];

    const defaultCategories = [
        { id: 1, defaultName: 'Игры', defaultIcon: 'Gamepad2' },
        { id: 2, defaultName: 'Аниме', defaultIcon: 'Tv' },
        { id: 3, defaultName: 'Фильмы', defaultIcon: 'Clapperboard' },
        { id: 4, defaultName: 'Манга', defaultIcon: 'BookOpen' },
        { id: 5, defaultName: 'Книги', defaultIcon: 'Book' },
        { id: 6, defaultName: 'Ранобэ', defaultIcon: 'ScrollText' },
    ];
    let customCategories = $state<{ id: number; name: string; icon: string }[]>([]);
    $effect(() => {
        const storedCustom = localStorage.getItem('sidebar-item-custom');
        const customMap = storedCustom ? JSON.parse(storedCustom) : {};
        
        customCategories = defaultCategories.map(cat => ({
            id: cat.id,
            name: customMap[cat.id]?.name || cat.defaultName,
            icon: customMap[cat.id]?.icon || cat.defaultIcon
        }));
    });

    const supportedSites = [
        'https://www.chitai-gorod.ru/', 'https://www.kinopoisk.ru/', 'https://www.litres.ru/',
        'https://remanga.org/', 'https://реманга.орг/', 'https://shikimori.io/',
        'https://store.steampowered.com/', 'https://mangalib.me/', 'https://mangalib.org/',
        'https://ranobelib.me/', 'https://hentailib.me/', 'https://anilib.me/', 'https://myanimelist.net/'
    ];

    let importProgress = $state({
        isRunning: false,
        current: 0,
        total: 0,
        success: 0,
        failed: 0
    });

    function saveCategoryChanges() {
        const customMap: Record<number, { name: string; icon: string }> = {};
        customCategories.forEach(cat => {
            customMap[cat.id] = { name: cat.name, icon: cat.icon };
        });
        
        localStorage.setItem('sidebar-item-custom', JSON.stringify(customMap));
        showToast('Настройки категорий успешно сохранены');
        
        window.dispatchEvent(new Event('sidebar-update'));
    }

    async function fetchHtmlFromUrl(url: string) {
        try {
            const res = await fetch(url, { method: 'GET', headers: { 'Accept': 'text/html' } });
            if (res.ok) return await res.text();
        } catch (e) {
            console.warn('Direct HTML fetch failed, fallback to proxy', e);
        }
        const proxyResText = api.fetchUrl(url);
        return proxyResText;
    }

    function showToast(message: string, type: 'success' | 'error' = 'success', duration = 3000) {
        toast = { show: true, message, type };
        setTimeout(() => toast.show = false, duration);
    }

    function clearAllLocalData() {
        try {
            STORAGE_KEYS.forEach(key => localStorage.removeItem(key));
            showToast('Локальные настройки очищены');
            window.dispatchEvent(new Event('sidebar-update'));
            confirmModal = { show: false, type: null };
        } catch {
            showToast('Ошибка при очистке локальных данных', 'error');
        }
    }

    async function clearDatabase() {
        try {
            api.clearDataBase();
            showToast('База данных успешно очищена');
            confirmModal = { show: false, type: null };
        } catch (error) {
            showToast('Не удалось очистить базу данных', 'error');
        }
    }

    async function handleExport() {
        try {
            const res = await api.exportDataBase();
            const blob = await res.blob();
            if ('showSaveFilePicker' in window) {
                try {
                    const fileHandle = await (window as any).showSaveFilePicker({
                        suggestedName: 'saveitall_backup.json',
                        types: [{ description: 'Файл базы данных JSON', accept: { 'application/json': ['.json'] } }],
                    });
                    const writable = await fileHandle.createWritable();
                    await writable.write(blob);
                    await writable.close();
                    showToast('База данных успешно сохранена');
                    return;
                } catch (err: any) {
                    if (err.name === 'AbortError') return;
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
            await api.importDataBase(formData);
            showToast('Данные успешно импортированы');
        } catch (error) {
            showToast('Ошибка импорта базы данных', 'error');
        } finally {
            target.value = '';
        }
    }

    const delay = (ms: number) => new Promise(res => setTimeout(res, ms));

    async function handleShikimoriSelect(event: Event) {
        const target = event.target as HTMLInputElement;
        if (!target.files || target.files.length === 0) return;

        const file = target.files[0];
        
        try {
            const text = await file.text();
            const items = JSON.parse(text);

            if (!Array.isArray(items)) {
                throw new Error('Неверный формат файла');
            }

            importSettingsModal = { show: true, fileData: items, selectedCategory: 'auto' };
            
        } catch (error) {
            showToast('Ошибка чтения файла Shikimori. Проверьте формат .json', 'error');
            console.error(error);
        } finally {
            target.value = '';
        }
    }

    async function startShikimoriImport() {
        const { fileData, selectedCategory } = importSettingsModal;
        importSettingsModal.show = false;

        if (!fileData) return;

        importProgress = { isRunning: true, current: 0, total: fileData.length, success: 0, failed: 0 };
        
        for (const item of fileData) {
            importProgress.current += 1;
            
            try {
                const typeStr = item.target_type.toLowerCase() + 's';
                const formattedTitle = item.target_title.replace(/\s+/g, '-').replace(/[,.]/g, '');
                const sourceUrl = `https://shikimori.io/${typeStr}/${item.target_id}-${formattedTitle}`;

                let finalCategory = selectedCategory;
                if (selectedCategory === 'auto') {
                    const t = item.target_type.toLowerCase();
                    finalCategory = t === 'anime' ? 'anime' : t === 'manga' ? 'manga' : t === 'ranobe' ? 'ranobe' : 'other';
                }

                let finalData = {
                    is_import: true,
                    category: finalCategory,
                    title: item.target_title_ru || item.target_title,
                    source_url: sourceUrl,
                    cover_url: '',
                    description: '',
                    rating: item.score || 0,
                    comment: item.text,
                    tags: []
                };

                const importer = findImporter(sourceUrl);
                if (importer) {
                    try {
                        let importedData: any;
                        if (importer.fetchAndParse) {
                            importedData = await importer.fetchAndParse(sourceUrl);
                        } else if (importer.parseHtml) {
                            const html = await fetchHtmlFromUrl(sourceUrl);
                            importedData = importer.parseHtml(html, sourceUrl);
                        }
                        
                        if (importedData) {
                            finalData.cover_url = importedData.cover_url || '';
                            if (importedData.description) {
                                finalData.description = importedData.description;
                            }
                        }
                    } catch (e) {
                        console.warn(`Не удалось спарсить страницу: ${sourceUrl}`);
                    }
                }
                await api.addNewItem({
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(finalData)
                });
                importProgress.success += 1;

            } catch (e) {
                importProgress.failed += 1;
            }

            await delay(1000); 
        }

        showToast(`Импорт завершен! Успешно: ${importProgress.success}, Ошибок: ${importProgress.failed}`);
        importProgress.isRunning = false;
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
        
        {#if activeTab === 'data'}
            <div in:fade={{ duration: 200 }} class="space-y-8">
                <div class="space-y-4">
                    <h2 class="text-lg font-semibold text-text-primary flex items-center gap-2">
                        <RotateCcw size={18} class="text-accent" /> Локальный кэш
                    </h2>
                    <button onclick={() => confirmModal = { show: true, type: 'local' }} class="w-full flex items-center justify-between p-4 rounded-xl bg-surface/50 border border-border-subtle hover:bg-surface-hover transition-all group">
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
                
                <div class="space-y-4">
                    <h2 class="text-lg font-semibold text-text-primary flex items-center gap-2">
                        <Database size={18} class="text-accent" /> Резервная копия БД
                    </h2>
                    <div class="grid gap-4 sm:grid-cols-2">
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

                <div class="space-y-4">
                    <h2 class="text-lg font-semibold text-danger flex items-center gap-2">
                        <AlertTriangle size={18} /> Опасная зона
                    </h2>
                    <button onclick={() => confirmModal = { show: true, type: 'db' }} class="w-full flex items-center justify-between p-4 rounded-xl bg-danger-soft/50 border border-danger/20 hover:bg-danger-soft transition-all group">
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

        {#if activeTab === 'import'}
            <div in:fade={{ duration: 200 }} class="space-y-8">
                <div class="space-y-4">
                    <h2 class="text-lg font-semibold text-text-primary flex items-center gap-2">
                        <CloudDownload size={18} class="text-accent" /> Импорт списков
                    </h2>
                    <p class="text-sm text-text-secondary">
                        Загрузите экспортированные списки из других сервисов. Приложение попытается автоматически подтянуть обложки и данные.
                    </p>

                    <div class="grid gap-4 mt-4">
                        <input type="file" accept=".json" class="hidden" bind:this={shikimoriInput} onchange={handleShikimoriSelect} disabled={importProgress.isRunning} />
                        
                        <div class="relative overflow-hidden rounded-xl border {importProgress.isRunning ? 'border-accent bg-accent/5' : 'border-border-subtle bg-surface/50 hover:bg-surface-hover'} transition-all">
                            {#if importProgress.isRunning}
                                <div class="absolute left-0 top-0 bottom-0 bg-accent/10 transition-all duration-300" style="width: {(importProgress.current / importProgress.total) * 100}%"></div>
                            {/if}

                            <div class="relative flex items-center justify-between p-4 z-10">
                                <div class="flex items-center gap-4">
                                    <div class="w-10 h-10 rounded-lg bg-[#242424] flex items-center justify-center text-white">
                                        <FileJson size={20} />
                                    </div>
                                    <div class="text-left">
                                        <h3 class="text-sm font-medium text-text-primary">Shikimori.io</h3>
                                        {#if importProgress.isRunning}
                                            <p class="text-xs text-accent font-medium mt-1">
                                                Обработка: {importProgress.current} из {importProgress.total} 
                                                <span class="text-success ml-2">✓ {importProgress.success}</span>
                                                {#if importProgress.failed > 0}
                                                    <span class="text-danger ml-2">✗ {importProgress.failed}</span>
                                                {/if}
                                            </p>
                                        {:else}
                                            <p class="text-xs text-text-muted mt-1">Загрузите файл резервной копии списка (.json)</p>
                                        {/if}
                                    </div>
                                </div>

                                <button 
                                    onclick={() => shikimoriInput.click()} 
                                    disabled={importProgress.isRunning}
                                    class="px-4 py-2 rounded-lg text-sm font-medium transition-all {importProgress.isRunning ? 'bg-surface-raised text-text-muted cursor-not-allowed' : 'bg-accent text-white hover:bg-accent/80 shadow-md shadow-accent/20'}"
                                >
                                    {importProgress.isRunning ? 'Загрузка...' : 'Выбрать файл'}
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    {#if importProgress.isRunning}
                        <div class="p-3 mt-2 rounded-lg bg-warning-soft border border-warning/20 flex gap-3 text-warning">
                            <AlertTriangle size={16} class="shrink-0 mt-0.5" />
                            <p class="text-xs">Пожалуйста, не закрывайте страницу. Процесс идет с задержкой (1 сек на элемент), чтобы избежать блокировки по IP от Shikimori.</p>
                        </div>
                    {/if}
                </div>
            </div>
        {/if}

        {#if activeTab === 'categories'}
            <div in:fade={{ duration: 200 }} class="space-y-6">
                <div class="space-y-1">
                    <h2 class="text-lg font-semibold text-text-primary flex items-center gap-2">
                        <Settings2 size={18} class="text-accent" /> Кастомизация меню
                    </h2>
                    <p class="text-sm text-text-secondary">Установите свои названия и иконки для разделов трекера.</p>
                </div>

                <div class="space-y-3 max-h-[420px] overflow-y-auto pr-1 custom-scrollbar">
                    {#each customCategories as cat (cat.id)}
                        <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 p-3 rounded-xl bg-surface/40 border border-border-subtle hover:bg-surface/60 transition-colors">
                            
                            <div class="flex items-center gap-2 shrink-0">
                                <div class="w-10 h-10 rounded-lg bg-surface-raised border border-border-subtle flex items-center justify-center text-accent">
                                    <svelte:component this={availableIcons[cat.icon]} size={20} />
                                </div>
                                <select 
                                    bind:value={cat.icon}
                                    class="bg-surface border border-border-subtle text-text-primary text-sm rounded-xl px-3 py-2 focus:outline-none focus:border-accent/50 cursor-pointer h-10 w-36"
                                >
                                    {#each Object.keys(availableIcons) as iconName}
                                        <option value={iconName}>{iconName}</option>
                                    {/each}
                                </select>
                            </div>

                            <div class="flex-1">
                                <input 
                                    type="text" 
                                    bind:value={cat.name} 
                                    class="w-full h-10 bg-surface border border-border-subtle text-text-primary text-sm rounded-xl px-4 focus:outline-none focus:border-accent/50 transition-colors"
                                    placeholder="Название категории"
                                />
                            </div>
                        </div>
                    {/each}
                </div>

                <div class="pt-2 border-t border-border-subtle flex justify-end">
                    <button 
                        onclick={saveCategoryChanges} 
                        class="w-full sm:w-auto px-6 py-2.5 bg-accent text-white rounded-xl hover:bg-accent/80 transition-all text-sm font-medium flex items-center justify-center gap-2 shadow-md shadow-accent/20"
                    >
                        <Check size={16} />
                        Сохранить изменения
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
                    <p class="text-sm text-text-muted mt-1">Версия 1.3.6</p>
                </div>
                <p class="text-sm text-text-secondary max-w-md leading-relaxed">
                    Персональный локальный трекер медиа-контента. Отслеживайте игры, аниме, фильмы, мангу, книги и ранобэ в одном удобном месте.
                </p>
                <a href="https://github.com/Aetorny/SaveItAll" target="_blank" rel="noopener noreferrer" class="flex items-center gap-2 px-6 py-3 bg-surface-raised border border-border-subtle rounded-xl hover:bg-surface-hover hover:border-text-muted transition-all">
                    <ExternalLink size={20} class="text-text-primary" />
                    <span class="text-sm font-medium text-text-primary">Исходный код на GitHub</span>
                </a>
            </div>
        {/if}
    </div>
</div>

{#if importSettingsModal.show}
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4" transition:fade={{ duration: 200 }}>
        <div class="absolute inset-0 modal-overlay" onclick={() => importSettingsModal.show = false}></div>
        <div class="relative w-full max-w-sm glass-panel-strong rounded-2xl p-6 shadow-2xl" transition:scale={{ duration: 350, easing: backOut, start: 0.9 }}>
            
            <div class="flex items-center gap-3 mb-6">
                <div class="w-10 h-10 rounded-full bg-accent/10 text-accent flex items-center justify-center">
                    <Settings2 size={20} />
                </div>
                <div>
                    <h3 class="text-lg font-bold text-text-primary">Настройка импорта</h3>
                    <p class="text-xs text-text-muted">Найдено элементов: {importSettingsModal.fileData?.length || 0}</p>
                </div>
            </div>
            
            <div class="space-y-4 mb-8">
                <label class="block text-sm font-medium text-text-secondary">В какую вкладку добавить данные?</label>
                <select 
                    bind:value={importSettingsModal.selectedCategory}
                    class="w-full bg-surface border border-border-subtle text-text-primary text-sm rounded-xl px-4 py-3 focus:outline-none focus:border-accent/50 transition-colors cursor-pointer"
                >
                    {#each categoryOptions as option}
                        <option value={option.id}>{option.label}</option>
                    {/each}
                </select>
                <p class="text-xs text-text-muted leading-relaxed">
                    «Автоматически» распределит список по вкладкам Аниме, Манга и Ранобэ, основываясь на данных от Shikimori.
                </p>
            </div>

            <div class="flex gap-3">
                <button 
                    onclick={() => importSettingsModal.show = false}
                    class="flex-1 px-4 py-2.5 bg-surface border border-border-subtle text-text-secondary rounded-xl hover:bg-surface-hover transition-all text-sm font-medium"
                >
                    Отмена
                </button>
                <button 
                    onclick={startShikimoriImport}
                    class="flex-1 px-4 py-2.5 bg-accent text-white rounded-xl hover:bg-accent/80 transition-all text-sm font-medium flex items-center justify-center gap-2"
                >
                    <CloudDownload size={16} />
                    Начать
                </button>
            </div>
        </div>
    </div>
{/if}

{#if confirmModal.show}
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4" transition:fade={{ duration: 200 }}>
        <div class="absolute inset-0 modal-overlay" onclick={() => confirmModal = {show: false, type: null}}></div>
        <div class="relative w-full max-w-md glass-panel-strong rounded-2xl p-6 shadow-2xl" transition:scale={{ duration: 350, easing: backOut, start: 0.9 }}>
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
                    Все локальные настройки будут удалены. База данных затронута не будет.
                {:else if confirmModal.type === 'db'}
                    <strong class="text-danger">Внимание!</strong> Вы собираетесь полностью очистить базу данных.
                {/if}
            </p>
            <div class="flex gap-3">
                <button onclick={() => confirmModal = {show: false, type: null}} class="flex-1 px-4 py-2.5 bg-surface border border-border-subtle text-text-secondary rounded-xl hover:bg-surface-hover transition-all duration-200 text-sm font-medium">
                    Отмена
                </button>
                <button onclick={confirmAction} class="flex-1 px-4 py-2.5 text-white rounded-xl transition-all duration-200 text-sm font-medium flex items-center justify-center gap-2 group {confirmModal.type === 'db' ? 'bg-danger hover:bg-danger/80' : 'bg-warning hover:bg-warning/80'}">
                    <Trash2 size={16} class="group-hover:scale-110 transition-transform" />
                    Очистить
                </button>
            </div>
        </div>
    </div>
{/if}

{#if toast.show}
    <div class="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 px-6 py-3 rounded-xl shadow-lg flex items-center gap-3 border {toast.type === 'error' ? 'bg-danger-soft text-danger border-danger/20' : 'bg-success-soft text-success border-success/20'}" transition:fly={{ y: 20, duration: 400, easing: quintOut }}>
        {#if toast.type === 'success'}<Check size={18} />{:else}<X size={18} />{/if}
        <span class="text-sm font-medium">{toast.message}</span>
    </div>
{/if}