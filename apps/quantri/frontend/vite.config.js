import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import frappeui from 'frappe-ui/vite'
import path from 'path'

export default defineConfig({
  plugins: [
    frappeui({ frappeProxy: true, lucideIcons: true, jinjaBootData: true, buildConfig: { indexHtmlPath: '../quantri/www/quantri_app.html', emptyOutDir: true, sourcemap: true } }),
    vue(),
  ],
  resolve: { alias: { '@': path.resolve(__dirname, 'src'), '@shared': path.resolve(__dirname, 'src/_shared') } },
  server: { fs: { allow: [path.resolve(__dirname, '..')] } },
})
