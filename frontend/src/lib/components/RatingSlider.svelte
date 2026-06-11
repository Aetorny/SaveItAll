<script lang="ts">
    import { Star } from 'lucide-svelte';

    export let value: number = 0;
    export let id: string = 'rating';

    function renderStars(rating: number = 0) {
        return Array.from({ length: 10 }, (_, i) => i < rating);
    }
</script>

<div class="space-y-3">
    <label class="block text-xs font-semibold text-text-muted uppercase tracking-wider" for={id}>
        Оценка <span class="text-text-secondary font-normal">{value}/10</span>
    </label>
    <div class="flex items-center gap-4">
        <input 
            {id}
            type="range" 
            min="0" 
            max="10" 
            step="1"
            bind:value 
            class="flex-1"
        />
        <div class="flex gap-0.5">
            {#each renderStars(value) as filled}
                <Star size={16} class={filled ? 'text-warning fill-warning' : 'text-text-muted/30'} />
            {/each}
        </div>
    </div>
</div>
