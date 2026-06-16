<script lang="ts">
    import '../app.css';
    import { onMount } from 'svelte';
    import { afterNavigate, goto } from '$app/navigation';
    import { dndzone } from 'svelte-dnd-action';
    import { 
        Gamepad2, Tv, Clapperboard, BookOpen, Book, ScrollText,
        Film, Music, Heart, Star, Compass, Flame,
        GripVertical, Settings, ChevronRight,
        Sparkles, ArrowUp
    } from 'lucide-svelte';

    import { page } from '$app/stores';
    import { fade, fly } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';
    import { api } from '$lib/api'
    import { base } from '$app/paths';

    const STORAGE_KEY = 'sidebar-item-order';
    const LAST_TAB_KEY = 'sidebar-last-tab';

    const defaultItems = [
        { id: 1, name: 'Игры', path: '/games', icon: Gamepad2, color: 'text-cat-games', bgColor: 'bg-purple-500/10', borderColor: 'border-purple-500/20', gradient: 'from-purple-500/20 to-transparent' },
        { id: 2, name: 'Аниме', path: '/anime', icon: Tv, color: 'text-cat-anime', bgColor: 'bg-pink-500/10', borderColor: 'border-pink-500/20', gradient: 'from-pink-500/20 to-transparent' },
        { id: 3, name: 'Фильмы', path: '/movies', icon: Clapperboard, color: 'text-cat-movies', bgColor: 'bg-amber-500/10', borderColor: 'border-amber-500/20', gradient: 'from-amber-500/20 to-transparent' },
        { id: 4, name: 'Манга', path: '/manga', icon: BookOpen, color: 'text-cat-manga', bgColor: 'bg-blue-500/10', borderColor: 'border-blue-500/20', gradient: 'from-blue-500/20 to-transparent' },
        { id: 5, name: 'Книги', path: '/books', icon: Book, color: 'text-cat-books', bgColor: 'bg-emerald-500/10', borderColor: 'border-emerald-500/20', gradient: 'from-emerald-500/20 to-transparent' },
        { id: 6, name: 'Ранобэ', path: '/light-novels', icon: ScrollText, color: 'text-cat-lightnovels', bgColor: 'bg-cyan-500/10', borderColor: 'border-cyan-500/20', gradient: 'from-cyan-500/20 to-transparent' },
    ];

    const sidebarPaths = defaultItems.map((item) => item.path);
    let items = $state([...defaultItems]);
    let hoveredItem = $state<number | null>(null);
    let isDragging = $state(false);
    let scrollProgress = $state(0);
    const ico_path = api.getIconPath();

    const flipDurationMs = 250;

    let mainContainer: HTMLElement | undefined;
    let showScrollTopButton = $state(false);

    const availableIcons: Record<string, any> = { 
        Gamepad2, Tv, Clapperboard, BookOpen, Book, ScrollText, Film, Music, Heart, Star, Compass, Flame 
    };

    afterNavigate((navigation) => {
        const fromRoute = navigation.from?.route?.id;
        const toRoute = navigation.to?.route?.id;

        if (!toRoute) return;

        const getRootSegment = (routeId: string | null | undefined) => {
            if (!routeId) return null;
            return routeId.split('/').filter(Boolean)[0] || null;
        };

        const fromRoot = getRootSegment(fromRoute);
        const toRoot = getRootSegment(toRoute);

        if (fromRoot !== toRoot && mainContainer) {
            mainContainer.scrollTop = 0;
        }

        if (sidebarPaths.includes(toRoute)) {
            saveLastTab(toRoute);
        }
    });

    function loadStoredOrder() {
        try {
            const storedCustom = localStorage.getItem('sidebar-item-custom');
            let customMap = storedCustom ? JSON.parse(storedCustom) : {};

            const localizedDefaults = defaultItems.map(item => {
                if (customMap[item.id]) {
                    return {
                        ...item,
                        name: customMap[item.id].name || item.name,
                        icon: availableIcons[customMap[item.id].icon] || item.icon
                    };
                }
                return item;
            });

            const stored = localStorage.getItem(STORAGE_KEY);
            if (!stored) {
                items = localizedDefaults;
                return;
            }
            const order = JSON.parse(stored);
            if (!Array.isArray(order)) {
                items = localizedDefaults;
                return;
            }
            const orderedItems = order
                .map((id: number) => localizedDefaults.find((item) => item.id === id))
                .filter(Boolean) as typeof defaultItems;

            if (orderedItems.length === defaultItems.length) {
                items = orderedItems;
            } else {
                items = localizedDefaults;
            }
        } catch {}
    }

    onMount(() => {
        loadStoredOrder();
        
        window.addEventListener('sidebar-update', loadStoredOrder);
        
        const currentPath = window.location.pathname;
        if (sidebarPaths.includes(currentPath)) {
            saveLastTab(currentPath);
        }

        return () => {
            window.removeEventListener('sidebar-update', loadStoredOrder);
        };
    });

    function saveStoredOrder(list: typeof defaultItems) {
        try {
            const order = list.map((item) => item.id);
            localStorage.setItem(STORAGE_KEY, JSON.stringify(order));
        } catch {
            // ignore storage failures
        }
    }

    function saveLastTab(path: string) {
        if (!sidebarPaths.includes(path)) return;
        try {
            localStorage.setItem(LAST_TAB_KEY, path);
        } catch {
            // ignore storage failures
        }
    }

    function handleScroll(e: Event) {
        const target = e.target as HTMLElement;
        const scrollTop = target.scrollTop;
        const scrollHeight = target.scrollHeight - target.clientHeight;
        scrollProgress = scrollHeight > 0 ? scrollTop / scrollHeight : 0;

        showScrollTopButton = scrollTop > 300;
    }

    function scrollToTop() {
        if (mainContainer) {
            mainContainer.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        }
    }

    onMount(() => {
        loadStoredOrder();
        
        const currentPath = window.location.pathname;
        if (sidebarPaths.includes(currentPath)) {
            saveLastTab(currentPath);
        }
    });

    function handleDndConsider(e: CustomEvent<{ items: typeof defaultItems }>) {
        items = e.detail.items;
        isDragging = true;
    }

    function handleDndFinalize(e: CustomEvent<{ items: typeof defaultItems }>) {
        items = e.detail.items;
        saveStoredOrder(items);
        isDragging = false;
    }

    function getCategoryLabel(path: string) {
        const item = items.find(i => i.path === path);
        return item?.name || 'Медиа';
    }

    let currentCategory = $derived(sidebarPaths.find(p => $page.url.pathname === p));
    let pageTitle = $derived(currentCategory ? getCategoryLabel(currentCategory) : '');
    let isSettingsPage = $derived($page.url.pathname === '/settings');
</script>

<div class="flex h-screen bg-void text-text-primary overflow-hidden">
    <div 
        class="scroll-indicator" 
        style="transform: scaleX({scrollProgress})"
    ></div>

    <aside class="w-20 bg-void-light border-r border-border-subtle flex flex-col shrink-0 z-20 relative transition-all duration-300">
        <div class="h-16 flex items-center justify-center border-b border-border-subtle relative overflow-hidden">
            <div class="absolute inset-0 bg-gradient-to-b from-accent/5 to-transparent"></div>
            <div class="relative w-10 h-10 rounded-xl accent-gradient flex items-center justify-center shadow-lg shadow-accent-glow animate-pulse-glow">
                <img src="{ico_path}" class="w-full h-full object-contain scale-125" alt="icon" />
            </div>
        </div>

        <nav
            class="flex-1 overflow-y-auto py-3 px-2 space-y-1 custom-scrollbar relative"
            use:dndzone={{ items, flipDurationMs, dropTargetStyle: {} }}
            onconsider={handleDndConsider}
            onfinalize={handleDndFinalize}
        >
            {#each items as item, index (item.id)}
                <!-- svelte-ignore a11y_no_static_element_interactions -->
                <div 
                    class="relative group"
                    onmouseenter={() => hoveredItem = item.id}
                    onmouseleave={() => hoveredItem = null}
                >
                    {#if $page.url.pathname === item.path}
                        <div class="sidebar-active-indicator"></div>
                    {/if}

                    <a
                        href="{base}{item.path}"
                        onclick={() => {
                            saveLastTab(item.path);
                            goto(`${base}/item.path`);
                        }}
                        class="flex flex-col items-center gap-1.5 p-2.5 rounded-xl transition-all duration-300 relative overflow-hidden {$page.url.pathname === item.path ? item.bgColor + ' ' + item.borderColor + ' border' : 'hover:bg-surface hover:border hover:border-border-subtle border border-transparent'}"
                        title={item.name}
                    >
                        {#if $page.url.pathname === item.path}
                            <div class="absolute inset-0 bg-gradient-to-b {item.gradient} pointer-events-none opacity-50"></div>
                            <div class="absolute inset-0 rounded-xl bg-gradient-to-b from-white/5 to-transparent pointer-events-none"></div>
                        {/if}

                        <svelte:component 
                            this={item.icon} 
                            size={22} 
                            class="{$page.url.pathname === item.path ? item.color : 'text-text-secondary group-hover:text-text-primary'} transition-all duration-300 {$page.url.pathname === item.path ? 'scale-110' : 'group-hover:scale-110'}" 
                        />
                        <span class="text-[10px] font-medium {$page.url.pathname === item.path ? 'text-text-primary' : 'text-text-muted group-hover:text-text-secondary'} transition-colors">{item.name}</span>
                    </a>

                    <div class="absolute -left-0.5 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-60 cursor-grab active:cursor-grabbing transition-all duration-200 hover:opacity-100">
                        <GripVertical size={12} class="text-text-muted" />
                    </div>
                </div>
            {/each}
        </nav>

        <div class="p-2 border-t border-border-subtle relative">
            <div class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-border-subtle to-transparent"></div>
            <a
                href="{base}/settings"
                onclick={() => goto(`${base}/settings`)}
                class="flex flex-col items-center gap-1.5 p-2.5 rounded-xl transition-all duration-300 relative overflow-hidden {$page.url.pathname === '/settings' ? 'bg-surface border border-border-subtle' : 'hover:bg-surface hover:border hover:border-border-subtle border border-transparent'}"
                title="Настройки"
            >
                {#if isSettingsPage}
                    <div class="absolute inset-0 bg-gradient-to-b from-accent/10 to-transparent pointer-events-none"></div>
                {/if}
                <Settings size={22} class="{$page.url.pathname === '/settings' ? 'text-accent scale-110' : 'text-text-secondary'} transition-all duration-300" />
                <span class="text-[10px] font-medium {$page.url.pathname === '/settings' ? 'text-text-primary' : 'text-text-muted'}">Настройки</span>
            </a>
        </div>
    </aside>

    <main bind:this={mainContainer} class="flex-1 overflow-y-auto custom-scrollbar relative" onscroll={handleScroll}>
        <div class="animated-bg">
            <div class="bg-orb bg-orb-1"></div>
            <div class="bg-orb bg-orb-2"></div>
            <div class="bg-orb bg-orb-3"></div>
        </div>

        <div class="relative z-10 p-6 md:p-8 max-w-7xl mx-auto min-h-screen">
            {#if pageTitle}
                <div class="mb-8 animate-fade-in-up category-header" in:fly={{ y: -20, duration: 0, easing: quintOut }}>
                    <div class="flex items-center gap-3 mb-2">
                        <h1 class="text-4xl font-bold tracking-tight text-gradient">{pageTitle}</h1>
                        <ChevronRight size={24} class="text-text-muted animate-bounce-subtle" />
                    </div>
                    <p class="text-text-secondary mt-1 text-sm flex items-center gap-2">
                        <Sparkles size={14} class="text-accent" />
                        Ваша коллекция медиа-контента
                    </p>
                </div>
            {/if}
            <slot />
        </div>

        {#if showScrollTopButton}
            <button
                onclick={scrollToTop}
                transition:fade={{ duration: 200 }}
                class="fixed bottom-6 right-6 z-50 p-3 rounded-xl bg-void-light border border-border-subtle text-text-secondary hover:text-text-primary hover:border-accent/50 shadow-lg shadow-black/50 hover:scale-110 active:scale-95 transition-all duration-200 group"
                title="Наверх"
            >
                <ArrowUp size={20} class="group-hover:-translate-y-0.5 transition-transform duration-200" />
            </button>
        {/if}
    </main>
</div>
