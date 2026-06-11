<script lang="ts">
    import { X, CheckCircle, AlertCircle, Info } from 'lucide-svelte';
    import { fly, fade } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';
    import { createEventDispatcher } from 'svelte';

    interface Props {
        message: string;
        type?: 'success' | 'error' | 'info';
    }

    let { message, type = 'info' }: Props = $props();

    const dispatch = createEventDispatcher<{ close: void }>();

    const icons = {
        success: CheckCircle,
        error: AlertCircle,
        info: Info
    };

    const styles = {
        success: 'bg-success-soft border-success/20 text-success',
        error: 'bg-danger-soft border-danger/20 text-danger',
        info: 'bg-surface border-border-subtle text-text-primary'
    };

    const iconColors = {
        success: 'text-success',
        error: 'text-danger',
        info: 'text-accent'
    };

    function handleClose() {
        dispatch('close');
    }
</script>

<div 
    class="flex items-center gap-3 px-4 py-3 rounded-xl border shadow-lg backdrop-blur-md min-w-[280px] max-w-md {styles[type]}"
    in:fly={{ x: 50, duration: 400, easing: quintOut }}
    out:fade={{ duration: 200 }}
    role="alert"
>
    <svelte:component this={icons[type]} size={18} class={iconColors[type]} />
    <span class="text-sm font-medium flex-1">{message}</span>
    <button 
        on:click={handleClose}
        class="w-6 h-6 rounded-full hover:bg-white/10 flex items-center justify-center transition-colors shrink-0"
    >
        <X size={14} />
    </button>
</div>
