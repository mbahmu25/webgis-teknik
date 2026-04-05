import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // Kita buat nanti
import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura' // Tema baru PrimeVue V4
import ToastService from 'primevue/toastservice';
import ConfirmationService from 'primevue/confirmationservice';
import { definePreset } from '@primevue/themes';
import './style.css' // Tailwind & Leaflet CSS masuk sini
import 'primeicons/primeicons.css' // Icon PrimeVue

const app = createApp(App)
const MyPreset = definePreset(Aura, {
    semantic: {
        primary: {
            50: '#fff1f2',
            100: '#ffe4e6',
            200: '#fecdd3',
            300: '#fda4af',
            400: '#fb7185',
            500: '#f43f5e', // Warna Utama (Default Button)
            600: '#e11d48',
            700: '#be123c',
            800: '#9f1239',
            900: '#881337',
            950: '#4c0519'
        }
    }
});
app.use(router)
app.use(PrimeVue, {
    theme: {
        preset: MyPreset,
        options: {
            prefix: 'p',
            darkModeSelector: 'false',
            cssLayer: false,
        },
    }
})
app.use(ToastService);        // <--- TAMBAHKAN INI
app.use(ConfirmationService); // <--- TAMBAHKAN INI

app.mount('#app')