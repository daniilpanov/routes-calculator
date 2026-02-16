function showGlobalAlert(message, type = "danger") {
    const container = document.getElementById("alertContainer");
    container.innerHTML = `<div class="alert alert-${type} alert-fixed alert-dismissible fade show" role="alert">
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Закрыть"></button>
    </div>`;
    container.classList.remove("d-none");

    setTimeout(() => {
        const alert = container.querySelector(".alert");
        if (alert) new bootstrap.Alert(alert).close();
    }, 3000);
    console.log(type, "-", message);
}
