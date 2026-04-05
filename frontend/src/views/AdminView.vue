<script setup>
import { ref, onMounted, nextTick } from 'vue';
import axios from 'axios';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// PrimeVue Components
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Dropdown from 'primevue/dropdown';
import InputNumber from 'primevue/inputnumber';
import Toast from 'primevue/toast';
import ConfirmDialog from 'primevue/confirmdialog';
import Toolbar from 'primevue/toolbar';
import Tag from 'primevue/tag';
import IconField from 'primevue/iconfield';
import InputIcon from 'primevue/inputicon';
import FileUpload from 'primevue/fileupload'; // Opsional jika mau pakai UI PrimeVue, disini pakai input native biar simpel

import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';

// --- CONFIG ---
// Sesuaikan dengan URL endpoint API Django Anda
const API_URL = 'http://127.0.0.1:8000/api/peran-ft/'; 
const KATEGORI_URL = 'http://127.0.0.1:8000/api/kategori/';

// --- STATE UTAMA ---
const toast = useToast();
const confirm = useConfirm();
const items = ref([]);
const categories = ref([]); // Untuk Dropdown Kategori
const loading = ref(false);
const productDialog = ref(false);
const isEditMode = ref(false);
const submitted = ref(false);

// --- OPTIONS SDGS (1-17) ---
// Membuat array [{label: 'SDG 1', value: 1}, ..., {label: 'SDG 17', value: 17}]
const sdgOptions = Array.from({ length: 17 }, (_, i) => ({
    label: `SDG ${i + 1}`,
    value: i + 1
}));

// Filter Search Table
const filters = ref({
    global: { value: null, matchMode: 'contains' }
});

// Form State (Sesuai Model Django PeranFT)
const form = ref({
    id: null,
    nama_kegiatan: '',
    tahun: new Date().getFullYear(),
    kategori: null,      // ID Kategori (ForeignKey)
    kategori_sdgs: null, // Integer 1-17
    abstrak: '',
    nama_mitra: '',
    lokasi_administratif: '',
    latitude: -7.7702732,  // Default Lat (Jogja/UGM)
    longitude: 110.3778507, // Default Lng (Jogja/UGM)
    url: '',
    foto: null,          // File Object
    foto_preview: null   // URL string untuk preview saat edit
});

// Map Picker Variables
let pickerMap = null;
let pickerMarker = null;

// --- API METHODS ---

const fetchCategories = async () => {
    try {
        const res = await axios.get(KATEGORI_URL);
        // Sesuaikan jika response API Django anda ada pagination (res.data.results) atau list langsung (res.data)
        const data = res.data.results || res.data;
        categories.value = data.map(c => ({
            label: c.nama, // Asumsi field di model KategoriKegiatan adalah 'nama'
            value: c.id
        }));
    } catch (e) { console.error("Gagal load kategori", e); }
};

const fetchData = async () => {
    loading.value = true;
    try {
        const res = await axios.get(API_URL);
        // Handle GeoJSON Response dari Django (django-rest-framework-gis)
        // Biasanya formatnya: { type: "FeatureCollection", features: [...] }
        const features = res.data.features || res.data; // fallback jika bukan geojson standard
        
        items.value = features.map(f => {
            // Ambil properties
            const props = f.properties;
            // Ambil koordinat dari geometry (GeoJSON: [lng, lat])
            const lng = f.geometry ? f.geometry.coordinates[0] : 110.3778507;
            const lat = f.geometry ? f.geometry.coordinates[1] : -7.7702732;

            return {
                id: f.id, // ID biasanya di root feature atau di properties
                ...props,
                lat: lat,
                lng: lng
            };
        });
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal mengambil data', life: 3000 });
        console.error(e);
    } finally {
        loading.value = false;
    }
};

// --- CRUD LOGIC ---

const openNew = () => {
    form.value = {
        id: null,
        nama_kegiatan: '',
        tahun: new Date().getFullYear(),
        kategori: null,
        kategori_sdgs: null,
        abstrak: '',
        nama_mitra: '',
        lokasi_administratif: '',
        latitude: -7.7702732,
        longitude: 110.3778507,
        url: '',
        foto: null,
        foto_preview: null
    };
    submitted.value = false;
    isEditMode.value = false;
    productDialog.value = true;
};

const editProduct = (item) => {
    // Mapping data dari table ke form
    // Pastikan field 'kategori' di item sesuai dengan value dropdown (ID)
    form.value = { 
        ...item,
        // Jika API mengembalikan object kategori nested, ambil ID-nya. Jika ID, biarkan.
        kategori: (typeof item.kategori === 'object' && item.kategori !== null) ? item.kategori.id : item.kategori,
        latitude: item.lat, 
        longitude: item.lng,
        foto: null, // Reset input file baru
        foto_preview: item.foto // Simpan URL foto lama untuk preview
    };
    isEditMode.value = true;
    productDialog.value = true;
};

// --- MAP LOGIC (LEAFLET) ---

const onDialogShow = () => {
    // Render map setelah dialog muncul (nextTick)
    nextTick(() => {
        initPickerMap();
    });
};

const initPickerMap = () => {
    if (pickerMap) {
        pickerMap.remove(); // Bersihkan map lama agar tidak duplikat
    }
    
    const center = [form.value.latitude, form.value.longitude];
    pickerMap = L.map('picker-map').setView(center, 15);
    
    L.tileLayer('https://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',{
        maxZoom: 20, subdomains:['mt0','mt1','mt2','mt3']
    }).addTo(pickerMap);

    // Marker draggable
    pickerMarker = L.marker(center, { draggable: true }).addTo(pickerMap);

    // Event saat marker digeser
    pickerMarker.on('dragend', (e) => {
        const { lat, lng } = e.target.getLatLng();
        form.value.latitude = lat;
        form.value.longitude = lng;
    });

    // Event saat peta diklik
    pickerMap.on('click', (e) => {
        const { lat, lng } = e.latlng;
        pickerMarker.setLatLng([lat, lng]);
        form.value.latitude = lat;
        form.value.longitude = lng;
    });
    
    // Fix render size bug di dalam modal
    setTimeout(() => { pickerMap.invalidateSize(); }, 200);
};

// --- FILE HANDLING ---
const onFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
        form.value.foto = file;
        // Preview lokal
        form.value.foto_preview = URL.createObjectURL(file);
    }
};

// --- SAVE DATA (POST/PATCH) ---

const saveProduct = async () => {
    submitted.value = true;

    // Validasi Field Wajib
    if (!form.value.nama_kegiatan || !form.value.kategori) {
        toast.add({ severity: 'warn', summary: 'Validasi', detail: 'Nama Kegiatan dan Kategori wajib diisi.', life: 3000 });
        return;
    }

    // Gunakan FormData karena ada ImageField
    const formData = new FormData();
    formData.append('nama_kegiatan', form.value.nama_kegiatan);
    formData.append('tahun', form.value.tahun);
    formData.append('kategori', form.value.kategori); // Kirim ID
    formData.append('abstrak', form.value.abstrak || '');
    formData.append('nama_mitra', form.value.nama_mitra || '');
    formData.append('lokasi_administratif', form.value.lokasi_administratif || '');
    formData.append('url', form.value.url || '');
    
    if (form.value.kategori_sdgs) {
        formData.append('kategori_sdgs', form.value.kategori_sdgs);
    }

    // Handle Koordinat untuk Django PointField
    // Django REST Framework GIS biasanya mengharapkan GeoJSON String untuk PointField jika pakai FormData
    const geoJsonPoint = JSON.stringify({
        type: "Point",
        coordinates: [parseFloat(form.value.longitude), parseFloat(form.value.latitude)]
    });
    formData.append('koordinat', geoJsonPoint);

    // Handle Foto (Hanya kirim jika user upload baru)
    if (form.value.foto instanceof File) {
        formData.append('foto', form.value.foto);
    }

    try {
        if (isEditMode.value) {
            // PATCH untuk update
            await axios.patch(`${API_URL}${form.value.id}/`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Data berhasil diperbarui', life: 3000 });
        } else {
            // POST untuk create
            await axios.post(API_URL, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Data berhasil ditambahkan', life: 3000 });
        }
        
        productDialog.value = false;
        fetchData(); // Refresh table
    } catch (e) {
        console.error(e);
        const errMsg = e.response?.data ? JSON.stringify(e.response.data) : 'Gagal menyimpan data';
        toast.add({ severity: 'error', summary: 'Error', detail: errMsg, life: 5000 });
    }
};

// --- DELETE ---
const confirmDeleteProduct = (item) => {
    confirm.require({
        message: `Apakah Anda yakin ingin menghapus "${item.nama_kegiatan}"?`,
        header: 'Konfirmasi Hapus',
        icon: 'pi pi-exclamation-triangle',
        rejectProps: { label: 'Batal', severity: 'secondary', outlined: true },
        acceptProps: { label: 'Hapus', severity: 'danger' },
        accept: async () => {
            try {
                await axios.delete(`${API_URL}${item.id}/`);
                toast.add({ severity: 'success', summary: 'Terhapus', detail: 'Data dihapus', life: 3000 });
                fetchData();
            } catch (e) {
                toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal menghapus data', life: 3000 });
            }
        }
    });
};

// Helper warna badge kategori (Opsional)
const getSeverity = (id) => 'info'; 

// Load data saat komponen di-mount
onMounted(() => {
    fetchData();
    fetchCategories();
});
</script>

<template>
    <div class="bg-gray-50 min-h-screen pb-10">
        
        <div class="bg-white shadow-sm border-b px-6 py-4 flex justify-between items-center mb-6">
            <h1 class="text-xl font-bold text-slate-800">Manajemen Peran FT UGM</h1>
            <Button label="Refresh Data" icon="pi pi-refresh" severity="secondary" outlined size="small" @click="fetchData" />
        </div>

        <div class="card max-w-[95%] mx-auto">
            <Toast />
            <ConfirmDialog />

            <Toolbar class="mb-4 rounded-xl border-none shadow-sm p-4 bg-white">
                <template #start>
                    <Button label="Tambah Kegiatan" icon="pi pi-plus" severity="success" class="mr-2" @click="openNew" />
                </template>
                <template #end>
                    <IconField>
                        <InputIcon><i class="pi pi-search" /></InputIcon>
                        <InputText v-model="filters['global'].value" placeholder="Cari Kegiatan..." />
                    </IconField>
                </template>
            </Toolbar>

            <DataTable 
                ref="dt" 
                :value="items" 
                dataKey="id" 
                :paginator="true" 
                :rows="10" 
                :filters="filters"
                paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown" 
                :rowsPerPageOptions="[5, 10, 25]"
                currentPageReportTemplate="{first} - {last} dari {totalRecords}"
                :loading="loading"
                class="shadow-sm rounded-xl overflow-hidden bg-white"
            >
                <Column header="Foto" style="width: 10%">
                    <template #body="slotProps">
                        <img v-if="slotProps.data.foto" :src="slotProps.data.foto" class="rounded shadow-sm w-16 h-12 object-cover border" />
                        <div v-else class="w-16 h-12 bg-gray-100 rounded flex items-center justify-center text-xs text-gray-400 border">No Img</div>
                    </template>
                </Column>

                <Column field="nama_kegiatan" header="Nama Kegiatan" sortable style="min-width: 14rem"></Column>
                <Column field="tahun" header="Tahun" sortable style="width: 8rem"></Column>
                
                <Column field="nama_mitra" header="Mitra" sortable style="min-width: 10rem"></Column>

                <Column header="Kategori & SDGs" style="min-width: 12rem">
                    <template #body="slotProps">
                        <div class="flex flex-col gap-1">
                            <Tag :value="slotProps.data.kategori_nama || slotProps.data.kategori" severity="info" class="w-fit" />
                            <Tag v-if="slotProps.data.kategori_sdgs" :value="'SDG ' + slotProps.data.kategori_sdgs" severity="warning" class="w-fit" />
                        </div>
                    </template>
                </Column>

                <Column :exportable="false" style="min-width: 8rem">
                    <template #body="slotProps">
                        <Button icon="pi pi-pencil" outlined rounded severity="info" class="mr-2" @click="editProduct(slotProps.data)" />
                        <Button icon="pi pi-trash" outlined rounded severity="danger" @click="confirmDeleteProduct(slotProps.data)" />
                    </template>
                </Column>
            </DataTable>
        </div>

        <Dialog 
            v-model:visible="productDialog" 
            :style="{ width: '900px' }" 
            :header="isEditMode ? 'Edit Kegiatan' : 'Tambah Kegiatan Baru'" 
            :modal="true" 
            class="p-fluid"
            @show="onDialogShow"
        >
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-2">
                
                <div class="flex flex-col gap-4">
                    
                    <div class="flex flex-col gap-2">
                        <label for="name" class="font-bold">Nama Kegiatan <span class="text-red-500">*</span></label>
                        <InputText id="name" v-model.trim="form.nama_kegiatan" required="true" :class="{'p-invalid': submitted && !form.nama_kegiatan}" />
                        <small class="p-error" v-if="submitted && !form.nama_kegiatan">Nama wajib diisi.</small>
                    </div>

                    <div class="flex gap-4">
                        <div class="flex-1 flex flex-col gap-2">
                            <label class="font-bold">Tahun</label>
                            <InputNumber v-model="form.tahun" :useGrouping="false" />
                        </div>
                        <div class="flex-1 flex flex-col gap-2">
                            <label class="font-bold">Kategori <span class="text-red-500">*</span></label>
                            <Dropdown 
                                v-model="form.kategori" 
                                :options="categories" 
                                optionLabel="label" 
                                optionValue="value" 
                                placeholder="Pilih Kategori" 
                                class="w-full" 
                                filter
                                :class="{'p-invalid': submitted && !form.kategori}"
                            />
                            <small class="p-error" v-if="submitted && !form.kategori">Pilih kategori.</small>
                        </div>
                    </div>

                    <div class="flex gap-4">
                        <div class="flex-1 flex flex-col gap-2">
                            <label class="font-bold">Kategori SDGs</label>
                            <Dropdown 
                                v-model="form.kategori_sdgs" 
                                :options="sdgOptions" 
                                optionLabel="label" 
                                optionValue="value" 
                                placeholder="Pilih SDG" 
                                filter
                            />
                        </div>
                        <div class="flex-1 flex flex-col gap-2">
                            <label class="font-bold">Nama Mitra</label>
                            <InputText v-model="form.nama_mitra" />
                        </div>
                    </div>

                    <div class="flex flex-col gap-2">
                        <label class="font-bold">Lokasi Administratif</label>
                        <InputText v-model="form.lokasi_administratif" placeholder="Contoh: Indonesia | DIY | Sleman" />
                    </div>

                    <div class="flex flex-col gap-2">
                        <label class="font-bold">URL Berita/Info</label>
                        <InputText v-model="form.url" placeholder="https://..." />
                    </div>

                    <div class="flex flex-col gap-2">
                        <label class="font-bold">Abstrak / Keterangan</label>
                        <Textarea v-model="form.abstrak" rows="3" cols="20" />
                    </div>

                    <div class="flex flex-col gap-2">
                        <label class="font-bold">Foto Kegiatan</label>
                        <div v-if="form.foto_preview" class="mb-2">
                            <img :src="form.foto_preview" class="h-24 w-auto rounded border shadow-sm" alt="Preview" />
                        </div>
                        <input type="file" @change="onFileSelect" accept="image/*" class="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-violet-50 file:text-violet-700 hover:file:bg-violet-100"/>
                    </div>
                </div>

                <div class="flex flex-col gap-2 h-full min-h-[400px]">
                    <label class="font-bold">Titik Lokasi (Geser Marker) <span class="text-red-500">*</span></label>
                    <div class="flex gap-2 mb-2">
                        <InputText v-model="form.latitude" placeholder="Latitude" class="w-1/2 bg-gray-50" />
                        <InputText v-model="form.longitude" placeholder="Longitude" class="w-1/2 bg-gray-50" />
                    </div>
                    
                    <div class="flex-1 border rounded-lg overflow-hidden relative shadow-inner bg-gray-100 h-full min-h-[350px]">
                        <div id="picker-map" class="absolute inset-0 w-full h-full z-0"></div>
                    </div>
                    <small class="text-gray-500">Klik peta atau geser marker untuk menentukan lokasi.</small>
                </div>
            </div>

            <template #footer>
                <Button label="Batal" icon="pi pi-times" text @click="productDialog = false" />
                <Button label="Simpan Data" icon="pi pi-check" @click="saveProduct" severity="success" />
            </template>
        </Dialog>

    </div>
</template>

<style scoped>
/* Pastikan Map Leaflet berada di bawah dialog PrimeVue jika ada masalah z-index */
.leaflet-pane {
    z-index: 0 !important;
}
/* Style tambahan untuk map control agar terlihat rapi */
.leaflet-top, .leaflet-bottom {
    z-index: 400 !important;
}
</style>