<script>
	import { createClient } from '@supabase/supabase-js';
	import { onMount } from 'svelte';
	import { SUPABASE_URL, SUPABASE_ANON_KEY } from '$lib/constants';
	import { goto } from '$app/navigation';
	import { io } from 'socket.io-client';
	import { Toast } from 'flowbite-svelte';
	// import L from 'leaflet';
	import 'leaflet/dist/leaflet.css';

	let access_token = null;
	let client = null;
	let connected = false;

	let flights = {};
	let command_status = '';
	let supabaseData = '';

	let map = null;
	let mapObjects = [];
	let planeIcon = null;
	let arucoIcon = null;

	let currentFlight = null;

	let L = null;

	$: ui_flights = () => Object.keys(flights).map((key) => ({ drone_id: key, ...flights[key] }));

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
				access_token = data.session.access_token;
				s_access_token = data.session.access_token;
				console.log('Access token found.');
			}

			const socket = io('http://100.75.51.60:4010/', {
				extraHeaders: {
					Authorization: `Bearer ${s_access_token}`
				}
			});

			socket.on('connect', function () {
				console.log('CONNECTED TO WEBSOCKET');
				connected = true;
			});

			socket.on('realtime_data', (data) => {
				console.log('Received realtime data');
				// console.log(data)

				flights[data.drone_id] = data;
			});

			function handleArmClick(drone_id) {
				return () => {
					console.log('handle arm');
					command_status = `Arming drone ${drone_id}...`;
					socket.emit('command_arm', drone_id);
				};
			}

			// Action for Disarm button
			function handleDisarmClick(drone_id) {
				return () => {
					console.log('handle disarm');
					command_status = `Arming drone ${drone_id}...`;
					socket.emit('command_disarm', drone_id);
				};
			}

			window.handleArmClick = handleArmClick;
			window.handleDisarmClick = handleDisarmClick;

			socket.on('realtime_data', (data) => {
				console.log('RECEIVED REALTIME_DATA:');
				console.log();
			});

			socket.on('active_flights', (data) => {
				console.log('RECEIVED ACTIVE_FLIGHTS:');
				console.log(data);
			});

			socket.on('drone_status', (data) => {
				console.log('RECEIVED DRONE_STATUS:');
				console.log(data);
			});

			socket.on('command_confirmation', (data) => {
				console.log('RECEIVED COMMAND_CONFIRMATION:');
				console.log(data);
			});

			socket.on('supabase_changed', () => {
				console.log('RECEIVED SUPABASE CHANGED');
				(async () => {
					const res = await fetch('http://100.75.51.60:4010/get_supabase_data');
					if (res.ok) {
						console.log('SUPABASE DATA:');
						console.log(await res.json());
					} else {
						console.log('ERROR');
						console.log(res);
					}
				})();
			});
			L = await import('leaflet');

			setupLeaflet();
		})();
	});

	async function onSupabaseClick() {
		console.log('ON SUPABASE CLICK');
		try {
			const res = await fetch('http://100.75.51.60:4010/get_supabase_data');
			const data = await res.json();
			if (data) {
				supabaseData = JSON.stringify(data);
			} else {
				throw 'No data received';
			}
		} catch (e) {
			alert(JSON.stringify(e));
		}
	}

	function setupLeaflet() {
		while (!L) {}
		if (L) {
			map = L.map('map').setView([20, 77], 5);
			L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
				attribution:
					'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
			}).addTo(map);

			planeIcon = L.icon({
				iconUrl: 'https://cdn-icons-png.flaticon.com/128/870/870143.png',
				iconSize: [20, 20],
				iconAnchor: [19, 19],
				popupAnchor: [0, -19]
			});

			arucoIcon = L.icon({
				iconUrl:
					'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAOEAAADhCAMAAAAJbSJIAAAAYFBMVEUAAAD////+/v5gYGClpaXc3NwFBQX7+/v4+PgICAgPDw9fX19jY2Pz8/PZ2dnS0tIVFRU7OzsjIyOEhIRYWFihoaHLy8tLS0t4eHiNjY1TU1Ozs7NISEjq6uqtra3V1dV6tf/gAAAEdUlEQVR4nO2daXPbIBBABbIEsuW4OZz0zv//lwU57XRqdjVaI+foez0+WMPCE8ieYQE1DQAAAAAAAAAAAACo9EM/NL14Nf3txau2mDNl8z9jWSHihFzf0Cxvqx5TZ0gFqwomPikRh2ZruqNaTJ1hyEPAWLjIdvaWLTecj6lwwQgXSALtRuR4m25p5Zgq93ngLK9xho2TGQ3P4VxMjS7p1f2m0VsTXFs95pzhGmBYNyaGa4Bh3ZgYrgGGdWNiuAYY1o2J4RpgWDcmhmuAYd2YGK4BhnVjYrgGGNaN+fENQ9j7mP4vcpoRfsnt/EXO2FyQzriuYXTey314Y7awtWYNQ+/DUyux+9zdHLpDd8bzc7rw9D4Mo3dKuTbVuS82JQ3h0diYa3/TBKcke3bO7UujOD25zu2Mjbn2N010jfylkfow+nBeygdvb8z1fy2Ucu2kUzDMH34UQ49hzdZgaImJIYZ1W4OhJSaGGNZtDYaWmBhiWLc1GFpiYohh3dZgaImJIYa1W2OdZrYa7qob5rzOl/M0wR++KrsR7sacaSilH8aHb6Jeaut3OW9x72KIpRlhex8O/Va9vpX3d4xKN5Va+dLWEJTcU4g5RVHZUNmFo+9CGl3wxfudp+BFiyQYong19WCsa5hG6SA79Hlnl1h2l/rDRf8vLu59TqXIvZT8ZWLlPuzV7XDJXfFvk16pD6dsrtyHcz2cgtY0HHp1D2V6SuWr7ZQROu+F3ErlOYx+L3diugHlkX/Rr4UV6bdrDTDEEEMMMcQQQwwxxBBDDDHE8FUNiysl35NhP2jH4bTOx9KMS4xh78RZjBmTpBKqztPMS8qKY578K81E+WljgTKfJuJOBa9omOeLFcPoiyuW/Q+nzfpqxFieTV1tlKpXH/LEWcFwn0eaTXCaEi6N8LUMh+b+KJ/p9DOPqNIzkz5/VMpp/MxzzFd8Dvum0+93kO730VjjgzTyX8dQIjVmY6xxnfyhDIYYLgfD2mCI4XIwrA2GGC4Hw9pgiOFyMKwNhhguB8PaYPjfGro3ZZiXCCuT910x9/JS67R+9vzzvEBYNuzVd3S00wrjmobTAmF5FXTTFXNdv01iLGVR8kT4jKG2srq4gvqiPlTTLwclEaillzRDrb6nnLUqHKN0QR+mP0elpW5fypOceNQDyyjVndaJ1zUctFOrgis+FSe6vFmjYNKrb+FIV5Tkm89bZmrvKFH6ULqjJ24a4Z1AvZY5TleU/Gnw5T016+3s0jCfAGioC0MMMcQQQwwxxBBDDDHEEEMMMcQQQwwxxBBDDDHEEEMMMcQQQwwxxBBDDDHEEEMMMcQQw+sY5hWwG9OBRz4bzqwSL9aYDJdXNp0BbjQcmo22JF3hubG8SrpX1whLhHwuj/VM9uZo7MObvF1BfK+AXGM2XErMd8X0PuB+2Jqfw0N+H/jy14EnQ/nEdqUPze901tbq63TSSnaV3vRNM2EzTBXejuIbNTTGp3xi3eJRmii+9UMnFxnvTIYAAAAAAAAAAAAAAPC2+AV5k2MW00GbdwAAAABJRU5ErkJggg==', // Replace with the URL of your plane icon
				iconSize: [25, 25],
				iconAnchor: [19, 19],
				popupAnchor: [0, -19]
			});
		}
	}

	$: {
		if (L) {
			console.log([flights, mapObjects]);
			let newMapObjects = [];
			let newMapObjectsFlights = [];
			for (const mapObject of mapObjects) {
				if (Object.keys(flights).includes(mapObject?.options?.title)) {
					console.log('found in mapobjects');
					const flight = flights[mapObject.options.title];
					mapObject.setLatLng([flight.lat, flight.lon]);
					newMapObjects.push(mapObject);
					newMapObjectsFlights.push(mapObject.options.title);
				} else {
					console.log('flight dropped');
					mapObject.remove();
				}
			}
			for (const flight of Object.values(flights)) {
				if (!newMapObjectsFlights.includes(flight.drone_id)) {
					console.log('flight not found in mapobjects');
					const marker = L.marker([flight.lat, flight.lon], {
						icon: planeIcon,
						title: flight.drone_id,
						click: onFlightClick
					})
						.addTo(map)
						.bindPopup(flight.drone_id)
						.openPopup()
						.on('click', () => onFlightClick(flight.drone_id));
					newMapObjects.push(marker);
					newMapObjectsFlights.push(flight.drone_id);
				}
			}
			mapObjects = newMapObjects;
		}
	}

	function onFlightClick(drone_id) {
		console.log('ON FLIGHT');
		console.log(flights);
		currentFlight = flights[drone_id];
	}
</script>

<!-- <style>
	#map {
		height: 180px;
		width: 180px;
	}
</style> -->

<!-- <svelte:head>
	<link
		rel="stylesheet"
		href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
		integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
		crossorigin=""
	/>
	<script
		src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
		integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
		crossorigin=""
	></script>
</svelte:head> -->

<h1 class="text-2xl font-black">Track</h1>

<div class="h-6"></div>

<div class="flex lg:flex-row md:flex-row sm:flex-col gap-2 overflow-x-auto pb-48">
	<div class="w-full bg-gray-200 rounded-md p-8">
		{#if currentFlight != null}
			<h1 class="text-2xl font-bold">{currentFlight.drone_id}</h1>
			<p>Flight ID: {currentFlight.flt_id}</p>
			<p>Latitude: {currentFlight.lat}</p>
			<p>Longitude: {currentFlight.lon}</p>
			<div class="h-4"></div>
			<h1 class="text-xl font-bold">Weather</h1>
			<p>Temperature: {currentFlight.temperature}</p>
			<p>Weather: {currentFlight.weather}</p>
			<p>Wind Direction: {currentFlight.wind_direction}</p>
			<!-- {else} -->
		{/if}
		{#if currentFlight == null}
			<p>No flight selected</p>
		{/if}
	</div>
	<div class="w-full">
		<div id="map" class="w-full h-96"></div>
		<div class="h-4"></div>
		<div class="weather">
			<iframe
				title="Weather Map"
				width="650"
				height="450"
				src="https://embed.windy.com/embed2.html?lat=23.623&lon=78.000&detailLat=20.000&detailLon=83.000&width=650&height=450&zoom=5&level=surface&overlay=wind&product=ecmwf&menu=&message=true&marker=true&calendar=12&pressure=&type=map&location=coordinates&detail=&metricWind=default&metricTemp=default&radarRange=-1"
				frameborder="0"
			>
			</iframe>
		</div>
	</div>
</div>

{#if connected && ui_flights().length == 0}
	<p>No flights connected</p>
{/if}

<!-- {#each ui_flights() as flight}
	<div class="display-box">
		<h1>{flight.drone_id}</h1>
		<p>Latitude: {flight.lat}</p>
		<p>Longitude: {flight.lon}</p>
		<p>Altitude: {flight.alt}</p>
		<div class="buttons">
			<button on:click={window.handleArmClick(flight.drone_id)}>Arm</button>
			<button on:click={window.handleDisarmClick(flight.drone_id)}>Disarm</button>
		</div>
	</div>
{/each} -->

<!-- <button on:click={onSupabaseClick}>Get Supabase Data</button>
<p>{supabaseData}</p>
{#if supabaseData != ''}
	<button on:click={() => (supabaseData = '')}>Hide Supabase Data</button>
{/if} -->

{#if !connected}
	<Toast position="bottom-right">Connecting to the WebSocket...</Toast>
{/if}
