/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Palet dari index.html (UGM Official)
        'ugm-blue': '#003366',      // Header background
        'ugm-dark': '#002244',      // Nav background
        'ugm-yellow': '#eab308',    // Aksen kuning/emas (approximate)
        
        // Palet dari greasV1.html (Teknik Identity)
        'teknik-green': '#0D5F46',  // Tombol & Aksen Teknik
        'teknik-green-hover': '#094532',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'], // Sesuai greasV1
      }
    },
  },
  plugins: [],
}