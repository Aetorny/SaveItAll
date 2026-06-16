<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { Loader2, Sparkles } from 'lucide-svelte';
    import { fade, scale } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';
    import { base } from '$app/paths';

    const sidebarPaths = ['/games', '/anime', '/movies', '/manga', '/books', '/light-novels'];
    const LAST_TAB_KEY = 'sidebar-last-tab';

    let loadingText = $state('Загрузка коллекции...');
    let dots = $state('');

    onMount(() => {
        // Animate loading dots
        const interval = setInterval(() => {
            dots = dots.length >= 3 ? '' : dots + '.';
        }, 500);

        let target = '/games';
        try {
            const stored = localStorage.getItem(LAST_TAB_KEY);
            if (stored && sidebarPaths.includes(stored)) {
                target = stored;
                loadingText = 'Возвращаемся к коллекции...';
            }
        } catch {
            // ignore storage access errors
        }

        // Slight delay for animation
        setTimeout(() => {
            goto(`${base}/${target}`, { replaceState: true });
        }, 800);

        return () => clearInterval(interval);
    });
</script>

<div class="flex flex-col items-center justify-center h-[60vh]" in:fade={{ duration: 300 }}>
    <div class="relative">
        <div class="absolute inset-0 bg-accent/10 blur-3xl rounded-full scale-150 animate-pulse"></div>
        <div class="absolute inset-0 bg-purple-500/10 blur-2xl rounded-full scale-125 animate-pulse" style="animation-delay: 0.5s"></div>

        <div class="relative w-16 h-16 flex items-center justify-center" in:scale={{ duration: 400, easing: quintOut, start: 0.5 }}>
            <Loader2 size={40} class="text-accent animate-spin relative" />
            <Sparkles size={16} class="text-accent/50 absolute top-0 right-0 animate-bounce-subtle" />
        </div>
    </div>

    <div class="mt-6 text-center" in:fade={{ duration: 400, delay: 200 }}>
        <p class="text-text-secondary text-sm font-medium">{loadingText}{dots}</p>
        <div class="mt-3 flex gap-1 justify-center">
            {#each [0, 1, 2] as i}
                <div 
                    class="w-1.5 h-1.5 rounded-full bg-accent/60"
                    style="animation: bounce-subtle 1s ease-in-out infinite; animation-delay: {i * 0.15}s"
                ></div>
            {/each}
        </div>
    </div>
</div>
