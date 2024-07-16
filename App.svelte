<script>
  import io from 'socket.io-client';
  import { onMount } from "svelte"

  // Define state variables for the display boxes
  let display1 = "";
  let display2 = "";
  let display3 = "";
  let flight_name = "";
  let id = "";

  let flights = []

  onMount(() => {
    localStorage.debug = "*"
    const socket = io('http://100.75.51.60:4010'); // Change the URL to your socket server

    // Connect to the socket server

    // Listen for socket events
    socket.on('redis_update', (data) => {
      console.log("Received redis update")
      console.log(data)
  
      let lat = ""
      let lon = ""
      let alt = ""

      const socket_data = Object.entries(data)
  
      for (const [flight_id, flight_data] of socket_data) { 
        // flights.push({
        //   flight_id,
        //   ...flight_data,
        // })
        if (flight_id == "Bullet_FOXTROT") {
          flight_name = flight_id
          lat = flight_data.lat
          lon = flight_data.lon
          alt = flight_data.alt
          id = flight_data.flt_id
        }
      }

      display1 = lat
      display2 = lon
      display3 = alt
    });
  })
  

  // Action for Arm button
  // function handleArmClick() {
  //   socket.emit('arm');
  // }

  // Action for Disarm button
  // function handleDisarmClick() {
  //   socket.emit('disarm');
  // }
</script>

<style>
  .container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
    margin-top: 50px;
  }

  /* .buttons {
    display: flex;
    gap: 10px;
  } */

  .display-box {
    width: 200px;
    height: 100px;
    border: 1px solid #ccc;
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;
    background-color: #f9f9f9;
    font-size: 1.2em;
  }
</style>

<div class="container">
  <!-- <div class="buttons">
    <button on:click={handleArmClick}>Arm</button>
    <button on:click={handleDisarmClick}>Disarm</button>
  </div> -->
  <div class="display-box">{"FLIGHT NAME: "+flight_name}</div>
  <div class="display-box">{"FLIGHT ID: "+id}</div>
  <div class="display-box">{"LAT: "+display1}</div>
  <div class="display-box">{"LONG: "+display2}</div>
  <div class="display-box">{"ALT: "+display3}</div>
</div>
