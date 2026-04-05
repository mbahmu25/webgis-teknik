<script setup>
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// --- 1. CONFIG & STATE ---
const API_URL = 'http://127.0.0.1:8000/api/peran-ft/'; 
const UGM_CENTER = [-7.7659, 110.3726];

const mapContainer = ref(null);
const locations = ref([]);        
const sidebarItems = ref([]);     
const loading = ref(false);
const selectedId = ref(null);     
const filters = ref({ tahun: '', kategori: '' });

const listTahun = [2024, 2023, 2022, 2021, 2020];
const listKategori = [
    { id: 1, nama: 'Pengabdian Masyarakat' }, 
    { id: 2, nama: 'Penelitian' }, 
    { id: 3, nama: 'Kerja Sama' }
];

// Variable Leaflet
let map = null;
let geoJsonLayer = null;
let markers = {}; 
let baseLayers = {}; // Untuk menyimpan layer agar bisa diakses custom control

// --- 2. LEAFLET LOGIC ---

import iconUrl from 'leaflet/dist/images/marker-icon.png';
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png';
import shadowUrl from 'leaflet/dist/images/marker-shadow.png';

const fixIcons = () => {
    delete L.Icon.Default.prototype._getIconUrl;
    L.Icon.Default.mergeOptions({ iconRetinaUrl, iconUrl, shadowUrl });
};

// Custom Popup Content (Disesuaikan dengan Style HTML Baru - Hijau)
const createPopup = (props) => {
    const img = props.foto_url 
        ? `<img src="${props.foto_url}" style="width:100%; height:120px; object-fit:cover; border-radius:4px 4px 0 0; margin-bottom:8px;">` 
        : `<div style="width:100%; height:80px; background:#f3f4f6; display:flex; align-items:center; justify-content:center; color:#9ca3af; font-size:10px;">No Image</div>`;
    
    // Ubah warna header menjadi #0D5F46 sesuai tema baru
    return `
        <div style="font-family: 'Inter', sans-serif; width:220px;">
            ${img}
            <div style="padding:0 4px;">
                <h3 style="margin:0; color:#0D5F46; font-size:13px; font-weight:bold; line-height:1.2;">${props.nama_kegiatan}</h3>
                <div style="font-size:10px; color:#666; margin:6px 0; display:flex; gap:6px;">
                    <span style="background:#eab308; color:white; padding:1px 4px; border-radius:2px; font-weight:bold;">${props.tahun}</span>
                    <span style="border-left:1px solid #ddd; padding-left:6px;">${props.kategori_nama || 'Umum'}</span>
                </div>
                <p style="font-size:10px; margin:4px 0; color:#444; line-height:1.4;">${props.abstrak ? props.abstrak.substring(0, 80) + '...' : '-'}</p>
            </div>
        </div>
    `;
};

const renderMap = (data) => {
    if (!map) return;
    
    if (geoJsonLayer) geoJsonLayer.clearLayers();
    markers = {}; 

    if (!data || !data.features) return;

    geoJsonLayer = L.geoJSON(data, {
        onEachFeature: (feature, layer) => {
            if (feature.properties) {
                layer.bindPopup(createPopup(feature.properties));
            }
            if (feature.id) {
                markers[feature.id] = layer;
                layer.on('click', () => {
                    selectedId.value = feature.id;
                    // Auto scroll sidebar logic could go here
                    const el = document.getElementById(`item-${feature.id}`);
                    if(el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                });
            }
        }
    }).addTo(map);

    if (data.features.length > 0) {
        map.fitBounds(geoJsonLayer.getBounds(), { padding: [50, 50] });
    }
};

// --- 3. DATA LOGIC ---
const fetchData = async () => {
    loading.value = true;
    try {
        const res = await axios.get(API_URL, { params: filters.value });
        locations.value = res.data;        
        sidebarItems.value = res.data.features || [];
        renderMap(locations.value);
    } catch (e) {
        console.error("Error fetch data:", e);
    } finally {
        loading.value = false;
    }
};

// Reset Filter Logic
const resetFilter = () => {
    filters.value = { tahun: '', kategori: '' };
};

// --- 4. INTERAKSI ---
const handleSidebarClick = (feature) => {
    selectedId.value = feature.id;
    const marker = markers[feature.id];
    
    if (marker) {
        map.flyTo(marker.getLatLng(), 17, { duration: 1.5 });
        marker.openPopup();
    }
};

// Custom Layer Control Logic (Untuk menggantikan UI bawaan Leaflet agar sesuai desain HTML)
const switchBaseLayer = (type) => {
    if(type === 'jalan') {
        baseLayers.satelit.remove();
        baseLayers.jalan.addTo(map);
    } else {
        baseLayers.jalan.remove();
        baseLayers.satelit.addTo(map);
    }
}

watch(filters, () => {
    fetchData();
}, { deep: true });

// --- 5. LIFECYCLE ---
onMounted(async () => {
    fixIcons();

    // Init Map
    map = L.map(mapContainer.value, { zoomControl: false }).setView(UGM_CENTER, 14);
    
    // Basemaps
    const satelit = L.tileLayer('https://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}', {
        maxZoom: 20, subdomains:['mt0','mt1','mt2','mt3'], attribution: 'Google Satellite'
    });
    const jalan = L.tileLayer('https://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
        maxZoom: 20, subdomains:['mt0','mt1','mt2','mt3'], attribution: 'Google Streets'
    });

    // Simpan referensi layer
    baseLayers = { satelit, jalan };
    jalan.addTo(map); // Default Jalan

    // Pindahkan Zoom Control ke kanan bawah (Sesuai HTML flow)
    L.control.zoom({ position: 'bottomright' }).addTo(map);

    await fetchData();
});
</script>

<template>
  <div class="bg-gray-100 h-screen flex flex-col font-sans">

    <nav class="bg-[#0e305d] border-b border-white/10 px-6 py-3 flex justify-between items-center shadow-lg z-30 relative">
        <div class="flex items-center gap-3">
            <img src="/logo.png"  alt="Logo UGM" class="h-10 w-10 object-contain">
            <h1 class="font-bold text-xl text-white tracking-tight">WebGIS FT UGM</h1>
        </div>

        <div class="hidden md:flex gap-8 text-sm font-medium text-gray-200">
            <a href="#" class="hover:text-yellow-400 transition-colors">Beranda</a>
            
            <a href="#" class="text-yellow-400 border-b-2 border-yellow-400 pb-1">Peta Interaktif</a>
            
            <a href="#" class="hover:text-yellow-400 transition-colors">Fasilitas</a>
            <a href="#" class="hover:text-yellow-400 transition-colors">Kontak</a>
        </div>

        <button class="bg-yellow-500 text-[#0e305d] px-6 py-2 rounded-lg font-bold hover:bg-yellow-400 transition shadow-md">
            MASUK
        </button>
    </nav>
    <main class="flex-1 flex overflow-hidden relative">
        
        <aside class="w-80 bg-white shadow-xl z-20 flex flex-col border-r">
            <div class="p-6 pb-0">
                <h2 class="text-[#0D5F46] font-bold text-xl mb-1">Peta Interaktif FT</h2>
                <p class="text-xs text-gray-500 mb-6">Visualisasi data sebaran kegiatan dan departemen di lingkungan Fakultas Teknik UGM.</p>

                <div class="border rounded-xl p-4 bg-gray-50 mb-6">
                    <div class="flex items-center gap-2 mb-4 text-gray-700 font-semibold text-sm">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                        </svg>
                        Filter Data
                    </div>
                    
                    <div class="space-y-3">
                        <div>
                            <label class="text-xs font-semibold text-gray-600 uppercase">Tahun Kegiatan</label>
                            <select v-model="filters.tahun" class="w-full mt-1 border rounded-md p-2 text-xs focus:ring-2 focus:ring-green-500 outline-none bg-white">
                                <option value="">Semua Tahun</option>
                                <option v-for="t in listTahun" :key="t" :value="t">{{ t }}</option>
                            </select>
                        </div>
                        <div>
                            <label class="text-xs font-semibold text-gray-600 uppercase">Kategori</label>
                            <select v-model="filters.kategori" class="w-full mt-1 border rounded-md p-2 text-xs focus:ring-2 focus:ring-green-500 outline-none bg-white">
                                <option value="">Semua Kategori</option>
                                <option v-for="k in listKategori" :key="k.id" :value="k.id">{{ k.nama }}</option>
                            </select>
                        </div>
                        <button @click="resetFilter" class="w-full border border-gray-300 py-2 rounded-md font-medium text-gray-600 text-xs hover:bg-gray-100 transition mt-2">
                            Reset Filter
                        </button>
                    </div>
                </div>

                <div class="flex justify-between items-center border-b pb-2 mb-2">
                    <span class="text-sm font-semibold text-gray-700">Hasil Pencarian</span>
                    <span class="font-bold text-sm text-[#0D5F46]">{{ sidebarItems.length }} Lokasi</span>
                </div>
            </div>

            <div class="flex-1 overflow-y-auto px-6 pb-6 space-y-3 custom-scrollbar">
                
                <div v-if="loading" class="text-center py-6 text-gray-400">
                    <div class="animate-spin h-5 w-5 border-2 border-[#0D5F46] border-t-transparent rounded-full mx-auto mb-2"></div>
                    <span class="text-xs">Memuat data...</span>
                </div>

                <div v-else-if="sidebarItems.length === 0" class="text-center py-6 text-gray-400 text-xs italic">
                    Data tidak ditemukan.
                </div>

                <div v-for="item in sidebarItems" :key="item.id" 
                     :id="`item-${item.id}`"
                     @click="handleSidebarClick(item)"
                     :class="['p-3 rounded-lg border bg-white cursor-pointer transition-all hover:shadow-md flex gap-3', 
                              selectedId === item.id ? 'ring-2 ring-[#0D5F46] border-transparent shadow-lg' : 'border-gray-200 shadow-sm']">
                    
                    <div class="w-14 h-14 bg-gray-200 rounded-md flex-none overflow-hidden border border-gray-100">
                        <img v-if="item.properties.foto_url" :src="item.properties.foto_url" class="w-full h-full object-cover">
                        <div v-else class="flex items-center justify-center h-full text-gray-400 text-[8px]">No Img</div>
                    </div>

                    <div class="flex-1 min-w-0">
                         <h3 class="font-bold text-xs text-gray-800 line-clamp-2 leading-tight mb-1 group-hover:text-[#0D5F46]">
                            {{ item.properties.nama_kegiatan }}
                        </h3>
                        <div class="flex items-center gap-2 mb-1">
                            <span class="text-[10px] bg-green-50 text-green-700 px-1.5 py-0.5 rounded font-medium border border-green-100">
                                {{ item.properties.tahun }}
                            </span>
                        </div>
                        <p class="text-[10px] text-gray-500 truncate">
                           {{ item.properties.kategori_nama || 'Umum' }}
                        </p>
                    </div>
                </div>

            </div>
            
            <div class="px-6 py-2 border-t text-[10px] text-gray-400 text-center">
                &copy; 2026 Teknik UGM Digital
            </div>
        </aside>

        <div class="flex-1 bg-gray-200 relative">
            <div ref="mapContainer" class="h-full w-full z-0"></div>

            <div class="absolute bottom-32 right-6 bg-white p-4 rounded-xl shadow-2xl border w-48 transition-all hover:scale-105 z-[400]">
                <p class="text-xs font-bold text-gray-700 mb-3 border-b pb-1 uppercase tracking-wider">Layer Peta</p>
                <div class="space-y-2 text-sm text-gray-600">
                    <label class="flex items-center gap-2 cursor-pointer hover:text-[#0D5F46]">
                        <input type="radio" name="layer" checked class="accent-[#0D5F46]" @change="switchBaseLayer('jalan')"> 
                        Peta Jalan
                    </label>
                    <label class="flex items-center gap-2 cursor-pointer hover:text-[#0D5F46]">
                        <input type="radio" name="layer" class="accent-[#0D5F46]" @change="switchBaseLayer('satelit')"> 
                        Satelit
                    </label>
                    <hr class="my-2">
                    <label class="flex items-center gap-2 cursor-pointer font-medium text-gray-800">
                        <input type="checkbox" checked class="rounded accent-[#0D5F46]"> Batas Kampus
                    </label>
                </div>
            </div>

            <div class="absolute bottom-6 right-6 bg-white p-4 rounded-xl shadow-2xl border w-48 z-[400]">
                <p class="text-xs font-bold text-gray-700 mb-3 border-b pb-1 uppercase tracking-wider">Legenda</p>
                <div class="space-y-2">
                    <div class="flex items-center gap-3">
                        <img :src="iconUrl" class="w-3 h-4 opacity-80">
                        <span class="text-xs text-gray-600">Lokasi Kegiatan</span>
                    </div>
                </div>
            </div>

        </div>

    </main>
  </div>
</template>

<style scoped>
/* Font Inter dari Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

.font-sans {
    font-family: 'Inter', sans-serif;
}

/* Custom Scrollbar agar rapi */
.custom-scrollbar::-webkit-scrollbar {
  width: 5px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>