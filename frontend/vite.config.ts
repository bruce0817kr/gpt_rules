import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const publicBasePath = process.env.VITE_PUBLIC_BASE_PATH || '/chat/';

export default defineConfig({
  base: publicBasePath,
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
  },
  preview: {
    host: '0.0.0.0',
    port: 4173,
  },
});
