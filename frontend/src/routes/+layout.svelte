<script>
    import '../app.css';
    import { onMount } from 'svelte';
    import { afterNavigate, goto } from '$app/navigation';
    import { dndzone } from 'svelte-dnd-action';
    import { Settings, Gamepad2, Tv, Clapperboard, BookOpen, Book, ScrollText } from 'lucide-svelte';
    import { page } from '$app/stores';

    const STORAGE_KEY = 'sidebar-item-order';
    const LAST_TAB_KEY = 'sidebar-last-tab';

    const defaultItems = [
        { id: 1, name: 'Игры', path: '/games', icon: Gamepad2 },
        { id: 2, name: 'Аниме', path: '/anime', icon: Tv },
        { id: 3, name: 'Фильмы', path: '/movies', icon: Clapperboard },
        { id: 4, name: 'Манга', path: '/manga', icon: BookOpen },
        { id: 5, name: 'Книги', path: '/books', icon: Book },
        { id: 6, name: 'Ранобэ', path: '/light-novels', icon: ScrollText },
    ];

    const sidebarPaths = defaultItems.map((item) => item.path);
    let items = [...defaultItems];

    const flipDurationMs = 200;

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
</script>

<div class="flex h-screen bg-gray-900 text-gray-200">
    <aside class="w-64 bg-gray-800 shadow-xl border-r border-gray-700 flex flex-col">
        <div class="p-4 text-xl font-bold border-b border-gray-700 text-white">Media Tracker</div>

        <nav
            class="flex-1 overflow-y-auto p-2 space-y-1"
            use:dndzone={{ items, flipDurationMs }}
            on:consider={handleDndConsider}
            on:finalize={handleDndFinalize}
        >
            {#each items as item (item.id)}
                <div class="animate-drop">
                    <a
                        href={item.path}
                        on:click|preventDefault={() => {
                            saveLastTab(item.path);
                            goto(item.path);
                        }}
                        class="flex items-center gap-3 px-3 py-2 rounded-md hover:bg-gray-700 transition-colors {$page.url.pathname === item.path ? 'bg-blue-600 text-white' : 'text-gray-300'}"
                    >
                        <svelte:component this={item.icon} size={20} />
                        {item.name}
                    </a>
                </div>
            {/each}
        </nav>

        <div class="p-2 border-t border-gray-700">
            <a
                href="/settings"
                class="flex items-center gap-3 px-3 py-2 rounded-md text-gray-300 hover:bg-gray-700 transition-colors {$page.url.pathname === '/settings' ? 'bg-blue-600 text-white' : ''}"
            >
                <Settings size={20} />
                Настройки
            </a>
        </div>
    </aside>

    <main class="flex-1 overflow-y-auto p-8">
        <slot />
    </main>
</div>