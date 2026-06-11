<script>
    import '../app.css';
    import { onMount } from 'svelte';
    import { afterNavigate, goto } from '$app/navigation';
    import { dndzone } from 'svelte-dnd-action';
    import { 
        Settings, 
        Gamepad2, 
        Tv, 
        Clapperboard, 
        BookOpen, 
        Book, 
        ScrollText,
        GripVertical
    } from 'lucide-svelte';
    import { page } from '$app/stores';

    const STORAGE_KEY = 'sidebar-item-order';
    const LAST_TAB_KEY = 'sidebar-last-tab';

    const defaultItems = [
        { id: 1, name: 'Игры', path: '/games', icon: Gamepad2, color: 'text-cat-games', bgColor: 'bg-purple-500/10', borderColor: 'border-purple-500/20' },
        { id: 2, name: 'Аниме', path: '/anime', icon: Tv, color: 'text-cat-anime', bgColor: 'bg-pink-500/10', borderColor: 'border-pink-500/20' },
        { id: 3, name: 'Фильмы', path: '/movies', icon: Clapperboard, color: 'text-cat-movies', bgColor: 'bg-amber-500/10', borderColor: 'border-amber-500/20' },
        { id: 4, name: 'Манга', path: '/manga', icon: BookOpen, color: 'text-cat-manga', bgColor: 'bg-blue-500/10', borderColor: 'border-blue-500/20' },
        { id: 5, name: 'Книги', path: '/books', icon: Book, color: 'text-cat-books', bgColor: 'bg-emerald-500/10', borderColor: 'border-emerald-500/20' },
        { id: 6, name: 'Ранобэ', path: '/light-novels', icon: ScrollText, color: 'text-cat-lightnovels', bgColor: 'bg-cyan-500/10', borderColor: 'border-cyan-500/20' },
    ];

    const sidebarPaths = defaultItems.map((item) => item.path);
    let items = [...defaultItems];

    const flipDurationMs = 250;

    function loadStoredOrder() {
        try {
            const stored = localStorage.getItem(STORAGE_KEY);
            if (!stored) return;
            const order = JSON.parse(stored);
            if (!Array.isArray(order)) return;
            const orderedItems = order
                .map((id) => defaultItems.find((item) => item.id === id))
                .filter(Boolean);
            if (orderedItems.length === defaultItems.length) {
                items = orderedItems;
            }
        } catch {
            // ignore invalid storage
        }
    }

    function saveStoredOrder(list) {
        try {
            const order = list.map((item) => item.id);
            localStorage.setItem(STORAGE_KEY, JSON.stringify(order));
        } catch {
            // ignore storage failures
        }
    }

    function saveLastTab(path) {
        if (!sidebarPaths.includes(path)) return;
        try {
            localStorage.setItem(LAST_TAB_KEY, path);
        } catch {
            // ignore storage failures
        }
    }

    onMount(() => {
        loadStoredOrder();
        const currentPath = window.location.pathname;
        if (sidebarPaths.includes(currentPath)) {
            saveLastTab(currentPath);
        }
        const unsubscribeAfter = afterNavigate(() => {
            const path = window.location.pathname;
            if (sidebarPaths.includes(path)) {
                saveLastTab(path);
            }
        });
        return () => {
            unsubscribeAfter?.();
        };
    });

    function handleDndConsider(e) {
        items = e.detail.items;
    }

    function handleDndFinalize(e) {
        items = e.detail.items;
        saveStoredOrder(items);
    }

    function getCategoryLabel(path) {
        const item = items.find(i => i.path === path);
        return item?.name || 'Медиа';
    }

    $: currentCategory = sidebarPaths.find(p => $page.url.pathname === p);
    $: pageTitle = currentCategory ? getCategoryLabel(currentCategory) : '';
</script>

<div class="flex h-screen bg-void text-text-primary overflow-hidden">
    <!-- Compact cinematic sidebar -->
    <aside class="w-20 bg-void-light border-r border-border-subtle flex flex-col shrink-0 z-20">
        <!-- Logo mark -->
        <div class="h-16 flex items-center justify-center border-b border-border-subtle">
            <div class="w-10 h-10 rounded-xl accent-gradient flex items-center justify-center shadow-lg shadow-accent-glow">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <polygon points="5 3 19 12 5 21 5 3"/>
                </svg>
            </div>
        </div>

        <!-- Navigation -->
        <nav
            class="flex-1 overflow-y-auto py-3 px-2 space-y-1 scrollbar-thin"
            use:dndzone={{ items, flipDurationMs, dropTargetStyle: {} }}
            on:consider={handleDndConsider}
            on:finalize={handleDndFinalize}
        >
            {#each items as item, index (item.id)}
                <div class="relative group">
                    <a
                        href={item.path}
                        on:click|preventDefault={() => {
                            saveLastTab(item.path);
                            goto(item.path);
                        }}
                        class="flex flex-col items-center gap-1.5 p-2.5 rounded-xl transition-all duration-200 relative {$page.url.pathname === item.path ? item.bgColor + ' ' + item.borderColor + ' border' : 'hover:bg-surface hover:border hover:border-border-subtle border border-transparent'}"
                        title={item.name}
                    >
                        {#if $page.url.pathname === item.path}
                            <div class="absolute inset-0 rounded-xl bg-gradient-to-b from-white/5 to-transparent pointer-events-none"></div>
                        {/if}
                        <svelte:component this={item.icon} size={22} class="{$page.url.pathname === item.path ? item.color : 'text-text-secondary group-hover:text-text-primary'} transition-colors" />
                        <span class="text-[10px] font-medium {$page.url.pathname === item.path ? 'text-text-primary' : 'text-text-muted group-hover:text-text-secondary'} transition-colors">{item.name}</span>
                    </a>
                    <!-- Drag handle indicator on hover -->
                    <div class="absolute -left-1 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-40 cursor-grab active:cursor-grabbing transition-opacity">
                        <GripVertical size={12} class="text-text-muted" />
                    </div>
                </div>
            {/each}
        </nav>

        <!-- Settings at bottom -->
        <div class="p-2 border-t border-border-subtle">
            <a
                href="/settings"
                on:click|preventDefault={() => goto('/settings')}
                class="flex flex-col items-center gap-1.5 p-2.5 rounded-xl transition-all duration-200 {$page.url.pathname === '/settings' ? 'bg-surface border border-border-subtle' : 'hover:bg-surface hover:border hover:border-border-subtle border border-transparent'}"
                title="Настройки"
            >
                <Settings size={22} class="{$page.url.pathname === '/settings' ? 'text-accent' : 'text-text-secondary'} transition-colors" />
                <span class="text-[10px] font-medium {$page.url.pathname === '/settings' ? 'text-text-primary' : 'text-text-muted'}">Настройки</span>
            </a>
        </div>
    </aside>

    <!-- Main content area -->
    <main class="flex-1 overflow-y-auto scrollbar-thin relative">
        <!-- Ambient background glow -->
        <div class="fixed inset-0 pointer-events-none overflow-hidden">
            <div class="absolute -top-40 -right-40 w-96 h-96 bg-accent/5 rounded-full blur-3xl"></div>
            <div class="absolute top-1/3 -left-20 w-64 h-64 bg-purple-500/5 rounded-full blur-3xl"></div>
        </div>

        <!-- Content -->
        <div class="relative z-10 p-8 max-w-7xl mx-auto">
            {#if pageTitle}
                <div class="mb-8 animate-fade-in">
                    <h1 class="text-4xl font-bold tracking-tight">{pageTitle}</h1>
                    <p class="text-text-secondary mt-1 text-sm">Ваша коллекция</p>
                </div>
            {/if}
            <slot />
        </div>
    </main>
</div>
