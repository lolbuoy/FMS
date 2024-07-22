<script>
	import { createClient } from '@supabase/supabase-js';
	import { onMount } from 'svelte';
	import { SUPABASE_URL, SUPABASE_ANON_KEY } from '../../lib/constants';
	import { goto } from '$app/navigation';

	let client = null;
	let sign_in_status = '';
	let sign_in_error = '';

	let email = '';
	let password = '';

	onMount(() => {
		const s_client = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

		client = s_client;

		(async () => {
			console.log('Checking existing session...');

			const { data, error } = await s_client.auth.getSession();
			if (error == null && data.session) {
				goto('/app/track');
			}
		})();
	});

	async function signIn() {
		sign_in_status = 'loading';
		const { data, error } = await client.auth.signInWithPassword({
			email,
			password
		});

		if (error) {
			sign_in_status = 'error';
			sign_in_error = 'Invalid login credentials';
		}

		if (data.session) {
			sign_in_status = 'success';
			goto('/app/track');
		}
	}
</script>

<main class="plain text-center">
	<h1 class="font-extrabold text-4xl">Sign In</h1>
	<div id="form">
		<label for="email">Email</label>
		<input name="email" type="email" bind:value={email} />

		<div class="spacer"></div>

		<label for="password">Password</label>
		<input name="password" type="password" bind:value={password} />

		<div class="spacer"></div>

		{#if sign_in_status == 'error'}
			<p class="error">{sign_in_error}</p>
			<div class="spacer"></div>
		{/if}

		{#if sign_in_status == 'loading'}
			<p>Signing in...</p>
			<div class="spacer"></div>
		{/if}

		<div class="h-4"></div>

		<button class="bg-primary-800 text-white py-2 shadow-md font-bold" on:click={signIn}>Sign In</button>
	</div>
</main>

<style>
	#form {
		display: flex;
		flex-direction: column;
		align-items: stretch;
		gap: 8px;
		margin: 36px;
	}

	#form > * {
		width: 100%;
	}
</style>
