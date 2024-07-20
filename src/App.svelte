<!-- <script>
    import { onMount } from 'svelte';
    import L from 'leaflet';

    let map;

    onMount(() => {
        map = L.map('map').setView([20, 77], 5);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(map);

        // Add marker for demonstration
        L.marker([28.7041, 77.1025]).addTo(map)
            .bindPopup('Delhi')
            .openPopup();
    });
</script> -->

<script lang="ts">
    import { onMount } from 'svelte';
    import L from 'leaflet';
    import 'leaflet/dist/leaflet.css';

    let map: L.Map;

    onMount(() => {
        map = L.map('map').setView([20, 77], 5);

        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        }).addTo(map);

        // // Custom icon
        // const customIcon = L.icon({
        //     iconUrl: 'https://leafletjs.com/examples/custom-icons/leaf-red.png',
        //     shadowUrl: 'https://leafletjs.com/examples/custom-icons/leaf-shadow.png',
        //     iconSize: [38, 95], // size of the icon
        //     shadowSize: [50, 64], // size of the shadow
        //     iconAnchor: [22, 94], // point of the icon which will correspond to marker's location
        //     shadowAnchor: [4, 62], // the same for the shadow
        //     popupAnchor: [-3, -76] // point from which the popup should open relative to the iconAnchor
        // });

        // // Add marker with custom icon
        // L.marker([28.7041, 77.1025], { icon: customIcon }).addTo(map)
        //     .bindPopup('ECHO')
        //     .openPopup();

        // Custom plane icon
        const planeIcon = L.icon({
            iconUrl: 'https://cdn-icons-png.flaticon.com/128/870/870143.png', // Replace with the URL of your plane icon
            iconSize: [20, 20], // size of the icon
            iconAnchor: [19, 19], // point of the icon which will correspond to marker's location
            popupAnchor: [0, -19] // point from which the popup should open relative to the iconAnchor
        });

        const arucoIcon = L.icon({
            iconUrl: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAOEAAADhCAMAAAAJbSJIAAAAYFBMVEUAAAD////+/v5gYGClpaXc3NwFBQX7+/v4+PgICAgPDw9fX19jY2Pz8/PZ2dnS0tIVFRU7OzsjIyOEhIRYWFihoaHLy8tLS0t4eHiNjY1TU1Ozs7NISEjq6uqtra3V1dV6tf/gAAAEdUlEQVR4nO2daXPbIBBABbIEsuW4OZz0zv//lwU57XRqdjVaI+foez0+WMPCE8ieYQE1DQAAAAAAAAAAAACo9EM/NL14Nf3txau2mDNl8z9jWSHihFzf0Cxvqx5TZ0gFqwomPikRh2ZruqNaTJ1hyEPAWLjIdvaWLTecj6lwwQgXSALtRuR4m25p5Zgq93ngLK9xho2TGQ3P4VxMjS7p1f2m0VsTXFs95pzhGmBYNyaGa4Bh3ZgYrgGGdWNiuAYY1o2J4RpgWDcmhmuAYd2YGK4BhnVjYrgGGNaN+fENQ9j7mP4vcpoRfsnt/EXO2FyQzriuYXTey314Y7awtWYNQ+/DUyux+9zdHLpDd8bzc7rw9D4Mo3dKuTbVuS82JQ3h0diYa3/TBKcke3bO7UujOD25zu2Mjbn2N010jfylkfow+nBeygdvb8z1fy2Ucu2kUzDMH34UQ49hzdZgaImJIYZ1W4OhJSaGGNZtDYaWmBhiWLc1GFpiYohh3dZgaImJIYa1W2OdZrYa7qob5rzOl/M0wR++KrsR7sacaSilH8aHb6Jeaut3OW9x72KIpRlhex8O/Va9vpX3d4xKN5Va+dLWEJTcU4g5RVHZUNmFo+9CGl3wxfudp+BFiyQYong19WCsa5hG6SA79Hlnl1h2l/rDRf8vLu59TqXIvZT8ZWLlPuzV7XDJXfFvk16pD6dsrtyHcz2cgtY0HHp1D2V6SuWr7ZQROu+F3ErlOYx+L3diugHlkX/Rr4UV6bdrDTDEEEMMMcQQQwwxxBBDDDHE8FUNiysl35NhP2jH4bTOx9KMS4xh78RZjBmTpBKqztPMS8qKY578K81E+WljgTKfJuJOBa9omOeLFcPoiyuW/Q+nzfpqxFieTV1tlKpXH/LEWcFwn0eaTXCaEi6N8LUMh+b+KJ/p9DOPqNIzkz5/VMpp/MxzzFd8Dvum0+93kO730VjjgzTyX8dQIjVmY6xxnfyhDIYYLgfD2mCI4XIwrA2GGC4Hw9pgiOFyMKwNhhguB8PaYPjfGro3ZZiXCCuT910x9/JS67R+9vzzvEBYNuzVd3S00wrjmobTAmF5FXTTFXNdv01iLGVR8kT4jKG2srq4gvqiPlTTLwclEaillzRDrb6nnLUqHKN0QR+mP0elpW5fypOceNQDyyjVndaJ1zUctFOrgis+FSe6vFmjYNKrb+FIV5Tkm89bZmrvKFH6ULqjJ24a4Z1AvZY5TleU/Gnw5T016+3s0jCfAGioC0MMMcQQQwwxxBBDDDHEEEMMMcQQQwwxxBBDDDHEEEMMMcQQQwwxxBBDDDHEEEMMMcQQw+sY5hWwG9OBRz4bzqwSL9aYDJdXNp0BbjQcmo22JF3hubG8SrpX1whLhHwuj/VM9uZo7MObvF1BfK+AXGM2XErMd8X0PuB+2Jqfw0N+H/jy14EnQ/nEdqUPze901tbq63TSSnaV3vRNM2EzTBXejuIbNTTGp3xi3eJRmii+9UMnFxnvTIYAAAAAAAAAAAAAAPC2+AV5k2MW00GbdwAAAABJRU5ErkJggg==', // Replace with the URL of your plane icon
            iconSize: [25, 25], // size of the icon
            iconAnchor: [19, 19], // point of the icon which will correspond to marker's location
            popupAnchor: [0, -19] // point from which the popup should open relative to the iconAnchor
        });

        // Add marker with custom plane icon
        L.marker([20.05123470, 83.62554790], { icon: planeIcon }).addTo(map)
            .bindPopup('ECHO')
            .openPopup();

        L.marker([13.174099, 77.741782], { icon: arucoIcon }).addTo(map)
            .bindPopup('HQ')
            .openPopup();    
    });
</script>


<style>
  .container {
      display: grid;
      grid-template-columns: 1fr 1fr;
      grid-gap: 20px;
      padding: 20px;
  }
  .card {
      background: black;
      border-radius: 10px;
      padding: 20px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
      border: 1px solid #ccc;
      border-radius: 5px;
      overflow: hidden;
  }
  .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
  }

  #map {
    /* height: 100%;
    width: 100%;  */
    height: 500px;
    width: 800px;
    }

  .map {
       
      background: black;
      border: 1px solid #ccc;
      border-radius: 5px;
      overflow: hidden;
  }
  
  .weather {
      height: 450px;
      width: 650px;
      border-radius: 10px;
      overflow: hidden;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }

  .grid-container {
      display: grid;
      grid-template-rows: 1 fr;
      grid-gap: 20px;
  } 
</style>

<div class="header">
  <div>
      <h1>Flight Monitoring System</h1>
      <h2>REDWING</h2>
  </div>
  <div>
      <input type="text" placeholder="Search..." />
  </div>
</div>

<div class="container">
  <div class="card">
      <h2>REDWING</h2>
      <!-- Flight details go here -->
      <div>
          <p>Flight No: KLF1322</p>
          <p>Aircraft Name & No: Bullet_ECHO</p>
          <p>Payload Weight: 300 gms</p>
          <p>Order ID: QF 123</p>
      </div>
      <div>
          <h3>Route</h3>
          <p>TMB to SBG</p>
          <p>Scheduled: 10:45 PM - 3:30 AM</p>
          <p>Actual: 9:04 AM - Estimated: 1:40 AM</p>
      </div>
      <div>
          <h3>Flight Details</h3>
          <p>MSL Altitude: 1500 m</p>
          <p>Air Speed: 20 m/s</p>
          <p>Ground Speed: 20 m/s</p>
          <p>GPS 1 Sat Count: 18</p>
          <p>GPS 2 Sat Count: 20</p>
          <p>Wind Speed and Direction: 3 m/s NE</p>
          <p>Battery Voltage: 49.2V</p>
          <p>Battery Current: 20A</p>
          <p>mAh Used: 32,000</p>
      </div>
  </div>
  <div class="grid-container">
    <div class="map">
        <div id="map"></div>
</div>
<div class="weather">
    <iframe 
        title="Weather Map" 
        width="650" 
        height="450" 
        src="https://embed.windy.com/embed2.html?lat=23.623&lon=78.000&detailLat=20.000&detailLon=83.000&width=650&height=450&zoom=5&level=surface&overlay=wind&product=ecmwf&menu=&message=true&marker=true&calendar=12&pressure=&type=map&location=coordinates&detail=&metricWind=default&metricTemp=default&radarRange=-1" 
        frameborder="0">
    </iframe>
</div>
</div>
</div>


