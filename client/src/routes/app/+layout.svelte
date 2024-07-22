<script>
	import { createClient } from '@supabase/supabase-js';
	import { onMount } from 'svelte';
	import { SUPABASE_URL, SUPABASE_ANON_KEY } from '$lib/constants';
	import { page } from '$app/stores';
	import { Navbar, NavBrand, NavHamburger, Drawer } from 'flowbite-svelte';
	import { Sidebar, SidebarGroup, SidebarItem, Toast } from 'flowbite-svelte';
	import { sineInOut } from 'svelte/easing';
	import { goto } from '$app/navigation';
	$: activeUrl = $page.url.pathname;

	let innerWidth = 0;

	let isMobile = true;
	let showDrawer = false;

	let logoutToast = ['', ''];
	let client = null;
	let access_token = '';

	$: hideDrawer = !showDrawer;
	$: {
		console.log([showDrawer, hideDrawer]);
	}

	$: if (innerWidth > 767) {
		// DESKTOP
		showDrawer = true;
		isMobile = false;

		// console.log(['desktop', innerWidth, showDrawer, isMobile]);
	} else {
		// MOBILE
		showDrawer = false;
		isMobile = true;

		// console.log(['mobile', innerWidth, showDrawer, isMobile]);
	}

	onMount(() => {
		const s_client = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
		client = s_client;

		(async () => {
			console.log('Checking existing session...');
			let s_access_token;

			const { data, error } = await s_client.auth.getSession();
			if (error != null) {
				goto('/auth');
			} else {
				if (data?.session?.access_token) {
					access_token = data.session.access_token;
					s_access_token = data.session.access_token;
					console.log('Access token found.');
				} else {
					goto('/auth');
				}
			}
		})();
	});

	function toggleDrawer() {
		console.log('toggle');
		console.log([showDrawer, !showDrawer]);
		showDrawer = !showDrawer;
	}

	async function onLogout() {
		console.log('Logout request');
		logoutToast = ['loading', ''];
		const { error } = await client.auth.signOut();

		if (error) {
			logoutToast = ['error', `Error logging out: ${JSON.stringify(error)}`];
		} else {
			console.log('LOGGED OUT');
			goto('/auth');
		}
	}
</script>

<svelte:window bind:innerWidth />

<div class="h-screen w-screen flex flex-col">
	<Navbar class="h-24 z-10" fluid>
		<NavBrand class="h-16 ml-4 flex-col items-start justify-center" href="/">
			<h3 class="text-2xl font-black">Redwing</h3>
			<sub class="text-small font-light">Flight Monitoring System</sub>
		</NavBrand>

		<NavHamburger onClick={toggleDrawer} />
	</Navbar>

	<div class="flex flex-row w-full h-full">
		<Drawer
			transitionType="fly"
			backdrop={false}
			bind:hidden={hideDrawer}
			activateClickOutside={false}
			transitionParams={{ delay: 100, duration: 200, easing: sineInOut }}
			leftOffset="start-0 h-screen flex pb-32 w-64"
		>
			<Sidebar {activeUrl} class="bg-white h-full flex flex-col justify-between" id="sidebar">
				<SidebarGroup>
					{#if isMobile}
						<!-- <button class="w-full text-center" on:click={toggleDrawer}>
							<CloseButton />
						</button> -->
					{/if}
					<SidebarItem label="Track Flights" href="/app/track" />
					<SidebarItem label="Order History" href="/app/orders" />
				</SidebarGroup>
				<SidebarGroup>
					<SidebarItem on:click={onLogout}>
						<svelte:fragment slot="subtext">Logout</svelte:fragment>
					</SidebarItem>
				</SidebarGroup>
			</Sidebar>
		</Drawer>

		{#if showDrawer}
			<div class="flex-grow w-72 h-screen">
				<p></p>
			</div>
			<div class="w-8"></div>
			<div class="w-8"></div>
		{/if}

		<main class="flex-grow w-full h-full bg-gray-50 p-6 z-0">
			<slot></slot>
		</main>
	</div>
</div>

{#if logoutToast[0] == 'loading'}
	<Toast position="bottom-right">Logging out...</Toast>
{/if}

{#if logoutToast[0] == 'error'}
	<Toast position="bottom-right">Error! {logoutToast[1]}</Toast>
{/if}

<style>
</style>
