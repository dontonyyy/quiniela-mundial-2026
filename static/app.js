document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".save-row-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var row = btn.closest(".match-row");
      var inputs = row.querySelectorAll("input[type=number]");
      var formData = new FormData();
      formData.append(btn.dataset.field1, inputs[0].value);
      formData.append(btn.dataset.field2, inputs[1].value);

      var originalText = btn.textContent;
      btn.disabled = true;
      btn.textContent = "...";
      btn.classList.remove("btn-error");

      fetch(btn.dataset.url, { method: "POST", body: formData })
        .then(function (r) { return r.json().then(function (data) { return { status: r.status, data: data }; }); })
        .then(function (res) {
          if (res.data.ok) {
            btn.textContent = "✓ Guardado";
            btn.classList.add("btn-ok");
            setTimeout(function () {
              btn.textContent = originalText;
              btn.classList.remove("btn-ok");
              btn.disabled = false;
            }, 1200);
          } else {
            btn.textContent = res.data.error || "Error";
            btn.classList.add("btn-error");
            btn.disabled = false;
          }
        })
        .catch(function () {
          btn.textContent = "Error de conexión";
          btn.classList.add("btn-error");
          btn.disabled = false;
        });
    });
  });
});
