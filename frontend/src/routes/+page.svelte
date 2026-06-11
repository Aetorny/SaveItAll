<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { Loader2 } from 'lucide-svelte';

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

<div class="flex flex-col items-center justify-center h-[60vh] animate-fade-in">
    <div class="relative">
        <div class="absolute inset-0 bg-accent/20 blur-2xl rounded-full"></div>
        <Loader2 size={40} class="text-accent animate-spin relative" />
    </div>
    <p class="text-text-secondary mt-4 text-sm">Загрузка коллекции...</p>
</div>
