import path from 'path';
import { fileURLToPath } from 'url';
import { defineConfig } from 'vitest/config';

const frontendRoot = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
    root: frontendRoot,
    test: {
        environment: 'jsdom',
        include: ['tests/**/*.test.js'],
        coverage: {
            provider: 'v8',
            include: ['js/lib/**/*.js'],
        },
    },
});
