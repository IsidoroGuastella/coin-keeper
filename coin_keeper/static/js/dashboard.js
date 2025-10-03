document.addEventListener("DOMContentLoaded", function() {
  const username = document.body.getAttribute("data-username"); 
  let i = 0;
  const speed = 50; // velocità in ms

  function typeWriter() {
    if (i < username.length) {
      document.getElementById("welcome-title").innerHTML += username.charAt(i);
      i++;
      setTimeout(typeWriter, speed);
    }
  }

  typeWriter();
});
