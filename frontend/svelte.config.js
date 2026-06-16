import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

const isDeploy = process.env.DEPLOY === 'true';

export default {
	preprocess: vitePreprocess(),
	kit: {
		adapter: adapter({
			pages: 'dist',
			assets: 'dist',
			fallback: 'index.html'
		}),
		paths: {
			base: isDeploy ? '/SaveItAll' : ''
		}
	}
};