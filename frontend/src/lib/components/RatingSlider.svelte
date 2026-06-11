<script lang="ts">
    import { Star } from 'lucide-svelte';

    interface Props {
        value?: number;
        id?: string;
    }

    let { value = $bindable(0), id = 'rating' }: Props = $props();

    let isHovering = $state(false);
    let hoverValue = $state(0);

    function renderStars(rating: number = 0) {
        return Array.from({ length: 10 }, (_, i) => i < rating);
    }

    function handleStarClick(index: number) {
        value = index + 1;
    }

    function handleStarHover(index: number) {
        hoverValue = index + 1;
    }

    function handleStarLeave() {
        hoverValue = value;
        isHovering = false;
    }

    let displayValue = $derived(isHovering ? hoverValue : value);
</script>

<div class="space-y-3">
    <label class="block text-xs font-semibold text-text-muted uppercase tracking-wider flex items-center gap-2" for={id}>
        <Star size={12} />
        Оценка <span class="text-text-secondary font-normal ml-1">{displayValue}/10</span>
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
            style="--value: {value * 10}%"
        />
        <div class="flex gap-0.5">
            {#each renderStars(displayValue) as filled, i}
                <button
                    type="button"
                    class="p-0.5 transition-all duration-150 hover:scale-125"
                    on:click={() => handleStarClick(i)}
                    on:mouseenter={() => { isHovering = true; handleStarHover(i); }}
                    on:mouseleave={handleStarLeave}
                >
                    <Star 
                        size={16} 
                        class="transition-colors duration-150 {filled ? 'text-warning fill-warning' : 'text-text-muted/30'}"
                    />
                </button>
            {/each}
        </div>
    </div>
</div>
