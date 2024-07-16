<script>
    // Define state variables for the display boxes
    let display1 = "Display Box 1";
    let display2 = "Display Box 2";
    let display3 = "Display Box 3";
  
    // Action for Button 1
    function handleButton1Click() {
      display1 = "Button 1 was clicked!";
      display2 = "Updated by Button 1";
      display3 = "Updated by Button 1";
    }
  
    // Action for Button 2
    function handleButton2Click() {
      display1 = "Button 2 was clicked!";
      display2 = "Updated by Button 2";
      display3 = "Updated by Button 2";
    }
  </script>
  
  <style>
    .container {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 20px;
      margin-top: 50px;
    }
  
    .buttons {
      display: flex;
      gap: 10px;
    }
  
    .display-box {
      width: 200px;
      height: 100px;
      border: 1px solid #ccc;
      display: flex;
      justify-content: center;
      align-items: center;
      background-color: #f9f9f9;
      font-size: 1.2em;
    }
  </style>
  
  <div class="container">
    <div class="buttons">
      <button on:click={handleButton1Click}>Button 1</button>
      <button on:click={handleButton2Click}>Button 2</button>
    </div>
    <div class="display-box">{display1}</div>
    <div class="display-box">{display2}</div>
    <div class="display-box">{display3}</div>
  </div>
  