type ToastType = 'success' | 'error' | 'info';

export interface ToastMessage {
    id: number;
    message: string;
    type: ToastType;
    duration?: number;
}

let toasts = $state<ToastMessage[]>([]);
let toastId = 0;

export const toastStore = {
    get toasts() {
        return toasts;
    },
    add(message: string, type: ToastType = 'info', duration = 3000) {
        const id = ++toastId;
        toasts = [...toasts, { id, message, type, duration }];
        setTimeout(() => this.remove(id), duration);
    },
    remove(id: number) {
        toasts = toasts.filter(t => t.id !== id);
    }
};

export function addToast(message: string, type: 'success' | 'error' | 'info' = 'info', duration = 3000) {
    const id = ++toastId;
    toasts = [...toasts, { id, message, type, duration }];
    setTimeout(() => {
        toasts = toasts.filter(t => t.id !== id);
    }, duration);
}