<html>
  <body>
    <!DOCTYPE html>

  <body>
  </body>

    <script>

      function sendDataToPython(data) {
        sendMessageToStreamlitClient("streamlit:setComponentValue", data);
      }

      // ----------------------------------------------------
      // Just copy/paste these functions as-is:

      function sendMessageToStreamlitClient(type, data) {
        var outData = Object.assign({
          isStreamlitMessage: true,
          type: type,
        }, data);
        window.parent.postMessage(outData, "*");
      }

      function init() {
        sendMessageToStreamlitClient("streamlit:componentReady", { apiVersion: 1 });
      }

      function setFrameHeight(height) {
        sendMessageToStreamlitClient("streamlit:setFrameHeight", { height: height });
      }

      // ----------------------------------------------------
      // Now modify this part of the code to fit your needs:
    // Timer functionality
    var timer;
    var timeoutDuration = 10000;
    const doc = window.parent.document;
    var wrapIframe = doc.querySelector('[title="inactiveuser.inactiveuser"]');
    wrapIframe.parentElement.style.height = '0px';

    const inputs = doc.querySelectorAll('textarea');
      inputs.forEach(input => {
    input.addEventListener('keydown', function(event) {
        // sendDataToPython({ value: "key" });
        resetTimer();
    });
        input.addEventListener('focus', function(event) {
        // sendDataToPython({ value: "focus" });
        resetTimer();
    });

    });


    function resetTimer() {
      clearTimeout(timer);
      timer = setTimeout(function() {
        sendDataToPython({ value: "timeout" });
      }, timeoutDuration);
    }


      // Hook things up!
      window.addEventListener("message", function (event) {
        if (event.data.type !== "streamlit:render") return;
        timeoutDuration = event.data.args.timeout;
      });
      init();

      // Hack to autoset the iframe height.
      window.addEventListener("load", function () {
        resetTimer();
        // sendDataToPython({ value: "init" });
        // sendDataToPython({ value: "timer" });
        // window.setTimeout(function () {
        //  setFrameHeight(0);
        // }, 0);
      });
      sendDataToPython({ value: "init" });

    </script>
  </body>
</html>
