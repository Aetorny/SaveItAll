<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    const sidebarPaths = ['/games', '/anime', '/movies', '/manga', '/books', '/light-novels'];
    const LAST_TAB_KEY = 'sidebar-last-tab';

    onMount(() => {
        let target = '/games';
        try {
            const stored = localStorage.getItem(LAST_TAB_KEY);
            if (stored && sidebarPaths.includes(stored)) {
                target = stored;
            }
        } catch {
            // ignore storage access errors
        }

        goto(target, { replaceState: true });
    });
</script>

<p class="text-gray-200">Перенаправление на последнюю открытую категорию...</p>