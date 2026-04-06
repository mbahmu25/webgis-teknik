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

import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';

// --- CONFIG ---
const API_URL = 'http://127.0.0.1:8000/api/peran-ft/'; 
const KATEGORI_URL = 'http://127.0.0.1:8000/api/kategori/';

// --- STATE UTAMA ---
const toast = useToast();
const confirm = useConfirm();
const items = ref([]);
const categories = ref([]);
const loading = ref(false);
const productDialog = ref(false);
const isEditMode = ref(false);
const submitted = ref(false);

// --- STATE KELOLA KATEGORI ---
const manageCategoryDialog = ref(false);
const newCategoryName = ref('');
const savingCategory = ref(false);

// --- OPTIONS SDGS (1-17) ---
const sdgOptions = Array.from({ length: 17 }, (_, i) => ({
    label: `SDG ${i + 1}`,
    value: i + 1
}));

// Filter Search Table
const filters = ref({
    global: { value: null, matchMode: 'contains' }
});

// Form State
const form = ref({
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
});

// Map Picker Variables
let pickerMap = null;
let pickerMarker = null;

// --- API METHODS ---

const fetchCategories = async () => {
    try {
        const res = await axios.get(KATEGORI_URL);
        const data = res.data.results || res.data;
        categories.value = data.map(c => ({
            label: c.nama, 
            value: c.id
        }));
    } catch (e) { console.error("Gagal load kategori", e); }
};

const fetchData = async () => {
    loading.value = true;
    try {
        const res = await axios.get(API_URL);
        const features = res.data.features || res.data; 
        
        items.value = features.map(f => {
            const props = f.properties;
            const lng = f.geometry ? f.geometry.coordinates[0] : 110.3778507;
            const lat = f.geometry ? f.geometry.coordinates[1] : -7.7702732;

            return {
                id: f.id, 
                ...props,
                lat: lat,
                lng: lng
            };
        });
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal mengambil data', life: 3000 });
    } finally {
        loading.value = false;
    }
};

// --- CRUD KATEGORI LOGIC ---

const openManageCategory = () => {
    newCategoryName.value = '';
    manageCategoryDialog.value = true;
    fetchCategories(); // Pastikan data terbaru
};

const saveCategory = async () => {
    if (!newCategoryName.value.trim()) {
        toast.add({ severity: 'warn', summary: 'Peringatan', detail: 'Nama kategori wajib diisi.', life: 3000 });
        return;
    }
    
    savingCategory.value = true;
    try {
        const res = await axios.post(KATEGORI_URL, { nama: newCategoryName.value });
        toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Kategori baru ditambahkan', life: 3000 });
        
        newCategoryName.value = ''; // Reset input
        await fetchCategories(); // Refresh list di table modal & dropdown
        
        // Auto-select di form utama jika form sedang terbuka
        const newCatId = res.data.id || (res.data.results && res.data.results.id);
        if (newCatId && productDialog.value) {
            form.value.kategori = newCatId;
        }
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal menyimpan kategori', life: 3000 });
    } finally {
        savingCategory.value = false;
    }
};

const deleteCategory = (id, name) => {
    confirm.require({
        message: `Hapus kategori "${name}"? Data kegiatan yang memakai kategori ini mungkin akan terdampak.`,
        header: 'Konfirmasi Hapus Kategori',
        icon: 'pi pi-exclamation-triangle',
        acceptProps: { label: 'Hapus', severity: 'danger' },
        rejectProps: { label: 'Batal', severity: 'secondary', outlined: true },
        accept: async () => {
            try {
                await axios.delete(`${KATEGORI_URL}${id}/`);
                toast.add({ severity: 'success', summary: 'Terhapus', detail: 'Kategori berhasil dihapus', life: 3000 });
                
                // Jika kategori yg dihapus sedang dipilih di form, reset dropdown-nya
                if (form.value.kategori === id) {
                    form.value.kategori = null;
                }
                
                fetchCategories(); // Refresh list
            } catch (e) {
                toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal menghapus kategori', life: 3000 });
            }
        }
    });
};

// --- CRUD KEGIATAN LOGIC ---

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
    form.value = { 
        ...item,
        kategori: (typeof item.kategori === 'object' && item.kategori !== null) ? item.kategori.id : item.kategori,
        latitude: item.lat, 
        longitude: item.lng,
        foto: null, 
        foto_preview: item.foto 
    };
    isEditMode.value = true;
    productDialog.value = true;
};

// --- MAP LOGIC (LEAFLET) ---

const onDialogShow = () => {
    nextTick(() => {
        initPickerMap();
    });
};

const initPickerMap = () => {
    if (pickerMap) pickerMap.remove(); 
    
    const center = [form.value.latitude, form.value.longitude];
    pickerMap = L.map('picker-map').setView(center, 15);
    
    L.tileLayer('https://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',{
        maxZoom: 20, subdomains:['mt0','mt1','mt2','mt3']
    }).addTo(pickerMap);

    pickerMarker = L.marker(center, { draggable: true }).addTo(pickerMap);

    pickerMarker.on('dragend', (e) => {
        const { lat, lng } = e.target.getLatLng();
        form.value.latitude = lat;
        form.value.longitude = lng;
    });

    pickerMap.on('click', (e) => {
        const { lat, lng } = e.latlng;
        pickerMarker.setLatLng([lat, lng]);
        form.value.latitude = lat;
        form.value.longitude = lng;
    });
    
    setTimeout(() => { pickerMap.invalidateSize(); }, 300);
};

// --- FILE HANDLING ---
const onFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
        form.value.foto = file;
        form.value.foto_preview = URL.createObjectURL(file);
    }
};

// --- SAVE DATA (POST/PATCH) ---

const saveProduct = async () => {
    submitted.value = true;

    if (!form.value.nama_kegiatan || !form.value.kategori) {
        toast.add({ severity: 'warn', summary: 'Validasi', detail: 'Nama Kegiatan dan Kategori wajib diisi.', life: 3000 });
        return;
    }

    const formData = new FormData();
    formData.append('nama_kegiatan', form.value.nama_kegiatan);
    formData.append('tahun', form.value.tahun);
    formData.append('kategori', form.value.kategori); 
    formData.append('abstrak', form.value.abstrak || '');
    formData.append('nama_mitra', form.value.nama_mitra || '');
    formData.append('lokasi_administratif', form.value.lokasi_administratif || '');
    formData.append('url', form.value.url || '');
    
    if (form.value.kategori_sdgs) {
        formData.append('kategori_sdgs', form.value.kategori_sdgs);
    }

    const geoJsonPoint = JSON.stringify({
        type: "Point",
        coordinates: [parseFloat(form.value.longitude), parseFloat(form.value.latitude)]
    });
    formData.append('koordinat', geoJsonPoint);

    if (form.value.foto instanceof File) {
        formData.append('foto', form.value.foto);
    }

    try {
        if (isEditMode.value) {
            await axios.patch(`${API_URL}${form.value.id}/`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Data berhasil diperbarui', life: 3000 });
        } else {
            await axios.post(API_URL, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Data berhasil ditambahkan', life: 3000 });
        }
        
        productDialog.value = false;
        fetchData(); 
    } catch (e) {
        const errMsg = e.response?.data ? JSON.stringify(e.response.data) : 'Gagal menyimpan data';
        toast.add({ severity: 'error', summary: 'Error', detail: errMsg, life: 5000 });
    }
};

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
                    <Button label="Kelola Kategori" icon="pi pi-tags" severity="info" outlined @click="openManageCategory" />
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
            :style="{ width: '800px' }" 
            :header="isEditMode ? 'Edit Kegiatan' : 'Tambah Kegiatan Baru'" 
            :modal="true" 
            class="p-fluid"
            @show="onDialogShow"
        >
            <div class="flex flex-col gap-6 mt-2">
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    
                    <div class="flex flex-col gap-2 md:col-span-2">
                        <label for="name" class="font-bold">Nama Kegiatan <span class="text-red-500">*</span></label>
                        <InputText id="name" v-model.trim="form.nama_kegiatan" required="true" :class="{'p-invalid': submitted && !form.nama_kegiatan}" />
                        <small class="p-error" v-if="submitted && !form.nama_kegiatan">Nama wajib diisi.</small>
                    </div>

                    <div class="flex flex-col gap-2">
                        <label class="font-bold">Tahun</label>
                        <InputNumber v-model="form.tahun" :useGrouping="false" />
                    </div>

                    <div class="flex flex-col gap-2">
                        <label class="font-bold">Kategori <span class="text-red-500">*</span></label>
                        <div class="flex gap-2">
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
                            <Button icon="pi pi-cog" severity="secondary" outlined @click="openManageCategory" v-tooltip.top="'Kelola Kategori'" />
                        </div>
                        <small class="p-error" v-if="submitted && !form.kategori">Pilih kategori.</small>
                    </div>

                    <div class="flex flex-col gap-2">
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

                    <div class="flex flex-col gap-2">
                        <label class="font-bold">Nama Mitra</label>
                        <InputText v-model="form.nama_mitra" />
                    </div>

                    <div class="flex flex-col gap-2">
                        <label class="font-bold">Lokasi Administratif</label>
                        <InputText v-model="form.lokasi_administratif" placeholder="Contoh: Indonesia | DIY | Sleman" />
                    </div>

                    <div class="flex flex-col gap-2">
                        <label class="font-bold">URL Berita/Info</label>
                        <InputText v-model="form.url" placeholder="https://..." />
                    </div>

                    <div class="flex flex-col gap-2 md:col-span-2">
                        <label class="font-bold">Abstrak / Keterangan</label>
                        <Textarea v-model="form.abstrak" rows="3" />
                    </div>

                    <div class="flex flex-col gap-2 md:col-span-2">
                        <label class="font-bold">Foto Kegiatan</label>
                        <div v-if="form.foto_preview" class="mb-2">
                            <img :src="form.foto_preview" class="h-24 w-auto rounded border shadow-sm" alt="Preview" />
                        </div>
                        <input type="file" @change="onFileSelect" accept="image/*" class="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-violet-50 file:text-violet-700 hover:file:bg-violet-100"/>
                    </div>
                </div>

                <div class="flex flex-col gap-2 border-t pt-4">
                    <label class="font-bold">Titik Lokasi (Geser Marker) <span class="text-red-500">*</span></label>
                    <div class="flex gap-2 mb-2">
                        <InputText v-model="form.latitude" placeholder="Latitude" class="w-1/2 bg-gray-50" />
                        <InputText v-model="form.longitude" placeholder="Longitude" class="w-1/2 bg-gray-50" />
                    </div>
                    
                    <div class="border rounded-lg overflow-hidden relative shadow-inner bg-gray-100 h-[350px]">
                        <div id="picker-map" class="absolute inset-0 w-full h-full z-0"></div>
                    </div>
                    <small class="text-gray-500">Klik peta atau geser marker untuk menentukan lokasi koordinat.</small>
                </div>

            </div>

            <template #footer>
                <Button label="Batal" icon="pi pi-times" text @click="productDialog = false" />
                <Button label="Simpan Data" icon="pi pi-check" @click="saveProduct" severity="success" />
            </template>
        </Dialog>

        <Dialog 
            v-model:visible="manageCategoryDialog" 
            :style="{ width: '500px' }" 
            header="Kelola Kategori" 
            :modal="true" 
            class="p-fluid"
        >
            <div class="flex flex-col gap-5 mt-2">
                <div class="flex flex-col gap-2 border bg-gray-50 p-4 rounded-lg">
                    <label for="new_category" class="font-bold text-sm">Tambah Kategori Baru</label>
                    <div class="flex gap-2">
                        <InputText 
                            id="new_category" 
                            v-model.trim="newCategoryName" 
                            placeholder="Ketik nama kategori..." 
                            @keyup.enter="saveCategory" 
                        />
                        <Button label="Simpan" icon="pi pi-plus" @click="saveCategory" :loading="savingCategory" severity="success" class="w-auto px-4" />
                    </div>
                </div>

                <div class="flex flex-col gap-2">
                    <label class="font-bold text-sm">Daftar Kategori Tersedia</label>
                    <DataTable :value="categories" scrollable scrollHeight="250px" size="small" class="border rounded-lg">
                        <Column field="label" header="Nama Kategori"></Column>
                        <Column header="Aksi" style="width: 5rem; text-align: center">
                            <template #body="slotProps">
                                <Button 
                                    icon="pi pi-trash" 
                                    severity="danger" 
                                    text 
                                    rounded 
                                    @click="deleteCategory(slotProps.data.value, slotProps.data.label)" 
                                    v-tooltip.left="'Hapus Kategori'"
                                />
                            </template>
                        </Column>
                        <template #empty>
                            <div class="text-center p-4 text-gray-500">Belum ada kategori.</div>
                        </template>
                    </DataTable>
                </div>
            </div>
            <template #footer>
                <Button label="Tutup" icon="pi pi-times" text @click="manageCategoryDialog = false" />
            </template>
        </Dialog>

    </div>
</template>

<style scoped>
.leaflet-pane {
    z-index: 0 !important;
}
.leaflet-top, .leaflet-bottom {
    z-index: 400 !important;
}
</style>